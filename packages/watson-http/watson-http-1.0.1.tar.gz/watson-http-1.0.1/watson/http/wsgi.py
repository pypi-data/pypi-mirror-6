# -*- coding: utf-8 -*-
import cgi
import collections
from io import BytesIO, BufferedReader
from urllib.parse import parse_qsl
from watson.common.contextmanagers import ignored
from watson.common.datastructures import MultiDict


__all__ = ['get_form_vars']


def read_binary(self):
    """Override for FieldStorage.read_binary method.

    Existing FieldStorage method raises a "TypeError: must be str, not bytes"
    when CONTENT_LENGTH is specified for a body that isn't key=value pairs.
    Decoding the data into the relevant encoding resolves the issue.
    """
    self.file = self.make_file()
    todo = self.length
    if todo >= 0:
        while todo > 0:
            data = self.fp.read(min(todo, self.bufsize))
            if not isinstance(data, bytes):
                raise ValueError("%s should return bytes, got %s"
                                 % (self.fp, type(data).__name__))
            self.bytes_read += len(data)
            if not data:
                self.done = -1
                break
            data = data.decode(self.encoding)  # The fix
            self.file.write(data)
            todo = todo - len(data)


cgi.FieldStorage.read_binary = read_binary


def get_form_vars(environ):
    """Convert environ vars into GET/POST/FILES objects.

    Process all get and post vars from a <form> and return MultiDict of
    each.
    """
    content_length = environ.get('CONTENT_LENGTH', '')
    length = int(content_length) if content_length else 0
    body = environ['wsgi.input'].read(length)
    environ['wsgi.body.original'] = body
    environ['wsgi.input'] = BufferedReader(BytesIO(body))

    if environ['REQUEST_METHOD'] == 'PUT' and not environ.get('CONTENT_TYPE'):
        environ['CONTENT_TYPE'] = 'application/x-www-form-urlencoded'
    field_storage = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ,
                                     keep_blank_values=True)
    get = MultiDict(
        ((name, value if value else '')
            for name, value
            in parse_qsl(environ.get('QUERY_STRING'), keep_blank_values=True)))
    get, post, files = _process_field_storage(field_storage, get=get)
    return get, post, files, body


File = collections.namedtuple(
    'File',
    'data filename name type type_options disposition disposition_options headers')


def _process_field_storage(fields, get=None, post=None, files=None):
    if not get:
        get = MultiDict()
    if not post:
        post = MultiDict()
    if not files:
        files = MultiDict()
    with ignored(Exception):
        for name in fields:
            field = fields[name] if isinstance(name, str) else name
            if isinstance(field, list):
                _process_field_storage(field, get, post, files)
            elif field.filename:
                # An uploaded file, create a new File tuple to resolve the
                # not indexable issue.
                files[field.name] = File(
                    field.file,
                    field.filename,
                    field.name,
                    field.type,
                    field.type_options,
                    field.disposition,
                    field.disposition_options,
                    field.headers)
            elif field.disposition or field.name not in get:
                post[field.name] = field.value
            else:
                pass  # pragma: no cover
    return get, post, files
