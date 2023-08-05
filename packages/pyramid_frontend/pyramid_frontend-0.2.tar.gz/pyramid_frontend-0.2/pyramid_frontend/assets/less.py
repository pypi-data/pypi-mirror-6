from __future__ import absolute_import, print_function, division

import os
import re

from webhelpers2.html.tags import HTML

from .compiler import Compiler


class LessCompiler(Compiler):
    """
    Compiler for LESS CSS files.
    """
    name = 'css'

    import_re = re.compile(r'@import[ ]+"(?P<path>.*)";')

    def compile(self, key, entry_point, output_dir, minify=True):
        """
        Compile a LESS entry point.
        """
        entry_point = self.theme.static_url_to_filesystem_path(entry_point)

        lessc_flags = []
        lessc_flags.append('--verbose')
        if minify:
            lessc_flags.append('--compress')

        with self.tempfile() as (in_fd, in_name):
            os.write(in_fd, self.concatenate(entry_point).encode('utf-8'))
            cmd = ['lessc'] + lessc_flags + [in_name]
            with self.tempfile() as (out_fd, out_name):
                cmd.append(out_name)
                self.run_command(cmd)
                file_path = self.write_from_file(key, out_name, entry_point,
                                                 output_dir)

        return file_path

    def concatenate(self, start_path):
        """
        Combine a LESS file and its `@import`s, recursively. Used to keep
        the ``lessc`` command-line compiler from having to traverse a directory
        structure, which it doesn't support very well right now.
        """
        err = 'File does not exist {0}'.format(start_path)
        assert os.path.isfile(start_path), err
        contents = []
        directory = os.path.dirname(start_path)
        with open(start_path) as fp:
            for line in fp:
                match = self.import_re.match(line.strip())
                if match:
                    path = match.groupdict()['path']
                    ext = os.path.splitext(path)[1]
                    if ext not in ('.css', '.less'):
                        path = '.'.join((path, 'less'))
                    if os.path.isabs(path):
                        path = self.theme.static_url_to_filesystem_path(path)
                    else:
                        path = os.path.join(directory, path)
                    contents.append(self.concatenate(path))
                else:
                    contents.append(line)
        return ''.join(contents)

    def tag_development(self, url):
        """
        Return an HTML fragment to use a less CSS entry point in development.
        """
        return ''.join([
            HTML.link(rel='stylesheet/less', type='text/css', href=url),
            HTML.script(src=self.theme.less_path),
        ])

    def tag_production(self, url):
        """
        Return an HTML fragment to use a less CSS entry point in production.
        """
        return HTML.link(rel='stylesheet', type='text/css', href=url)
