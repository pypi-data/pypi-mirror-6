from __future__ import absolute_import, print_function, division

import re
import posixpath
import os.path

from mako.exceptions import TopLevelLookupException
from mako.lookup import TemplateLookup


class SuperTemplateLookup(TemplateLookup):
    super_delimiter = '::'

    def find_dir_for(self, filename):
        for dir in self.directories:
            if os.path.commonprefix([filename, dir]) == dir:
                return dir
        raise ValueError("filename %r is not in any of this lookup's "
                         "directories" % filename)

    def get_template(self, uri):
        try:
            if self.filesystem_checks:
                return self._check(uri, self._collection[uri])
            else:
                return self._collection[uri]

        except KeyError:

            if self.super_delimiter in uri:
                file_path, from_dir = uri.split(self.super_delimiter)
                start_index = self.directories.index(from_dir) + 1
            else:
                start_index = 0
                file_path = uri

            u = re.sub(r'^\/+', '', file_path)
            for dir in self.directories[start_index:]:
                srcfile = posixpath.normpath(posixpath.join(dir, u))
                if os.path.isfile(srcfile):
                    return self._load(srcfile, uri)
            else:
                raise TopLevelLookupException(
                    "Cant locate template for uri %r" % uri)

    def adjust_uri(self, uri, relativeto):
        if uri.startswith('super:'):
            uri = uri[6:]
            relative_templ = self.get_template(relativeto)
            from_dir = self.find_dir_for(relative_templ.filename)
            assert from_dir, "can't find what dir calling template is in"
        else:
            from_dir = None

        uri = TemplateLookup.adjust_uri(self, uri, relativeto)
        if from_dir:
            return uri + self.super_delimiter + from_dir
        else:
            return uri
