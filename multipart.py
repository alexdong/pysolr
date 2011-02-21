#!/usr/bin/env python

import itertools
import mimetools
import mimetypes
from cStringIO import StringIO
import urllib
import urllib2

class MultiPartForm(object):
    """
    Accumulate the data to be used when posting a form.
    http://blog.doughellmann.com/2009/07/pymotw-urllib2-library-for-opening-urls.html
    """

    def __init__(self):
        self.form_fields = []
        self.files = []
        self.boundary = mimetools.choose_boundary()

    def get_content_type(self):
        return 'multipart/form-data; boundary=%s' % self.boundary

    def add_field(self, name, value):
        """Add a simple field to the form data."""
        self.form_fields.append((name, value))

    def add_file(self, fieldname, filename, content, mimetype=None):
        """Add a file to be uploaded."""
        if mimetype is None:
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        self.files.append((fieldname, filename, mimetype, content))

    def _safe_str(self, value):
        """
        Convert the value into str. If the value is an iterable container,
        convert each element first.
        """
        if type(value) != str:
            if type(value) == unicode:
                value = value.encode('utf-8')
            elif type(value) in (int, float, long):
                value = str(value)
            elif type(value) in (list, tuple):
                unicode_value = [self._safe_str(elem) for elem in value]
                value = ' '.join(unicode_value)
        return value


    def __str__(self):
        """Return a string representing the form data, including attached files."""
        # Build a list of lists, each containing "lines" of the
        # request.  Each part is separated by a boundary string.
        # Once the list is built, return a string where each
        # line is separated by '\r\n'.
        parts = []
        part_boundary = '--' + self.boundary

        # Add the form fields. Make sure the value fields have been
        # converted to str properly. This includes convert list/tuple
        # and numbers. Unicode will be utf-8 encoded str.
        parts.extend([
            part_boundary,
            'Content-Disposition: form-data; name="%s"' % \
                self._safe_str(name),
            '',
            self._safe_str(value),
            ] for name, value in self.form_fields)

        # Add the files to upload
        parts.extend([
            part_boundary,
            'Content-Disposition: form-data; name="%s"; filename="%s"' % \
                    (self._safe_str(field_name), self._safe_str(filename)),
            'Content-Type: %s' % (self._safe_str(content_type)),
            '',
            body,
            ] for field_name, filename, content_type, body in self.files)

        # Flatten the list and add closing boundary marker,
        # then return CR+LF separated data
        flattened = list(itertools.chain(*parts))
        flattened.append('--' + self.boundary + '--')
        flattened.append('')
        return '\r\n'.join(flattened)
