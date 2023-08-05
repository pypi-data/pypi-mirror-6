from __future__ import absolute_import, print_function, division

import logging

import os

from webhelpers2.html.tags import HTML

from .compiler import Compiler

log = logging.getLogger(__name__)


js_preamble = '''\
<script>
  if (typeof console === 'undefined') {
    console = {
      log: function () {},
      debug: function () {}
    }
  }
</script>
'''


def render_js_paths(theme):
    """
    Return a script tag for use client-side which sets up require.js paths for
    all theme directories in use by the supplied theme.
    """
    cls = theme.__class__
    keys = []
    while hasattr(cls, 'key'):
        keys.append(cls.key)
        cls = cls.__bases__[0]
    lines = ["require.paths.%s = '/_%s/js';" % (key, key)
             for key in keys]
    return ''.join(['<script>'] + lines + ['</script>'])


class RequireJSCompiler(Compiler):
    """
    Compile require.js javascript for theme. Assumes r.js is on $PATH.
    """

    name = 'js'

    def compile(self, key, entry_point, output_dir, minify=True):
        main_config = self.theme.static_url_to_filesystem_path(
            self.theme.require_config_path)
        base_url = self.theme.static_url_to_filesystem_path(
            self.theme.require_base_url)

        log.debug("base_url: %r", base_url)
        log.debug("main_config: %r", main_config)

        # Path to main module relative to baseUrl (can't be absolute)
        main_js_file = self.theme.static_url_to_filesystem_path(entry_point)
        main = os.path.relpath(main_js_file, base_url)
        main = os.path.splitext(main)[0]  # Strip .js

        almond_path = \
            self.theme.static_url_to_filesystem_path('/_pfe/almond.js')
        almond_path = os.path.relpath(almond_path, base_url)
        almond_path = os.path.splitext(almond_path)[0]

        log.debug("main: %r", main)

        cmd = [
            'r.js', '-o',
            'baseUrl={0}'.format(base_url),
            'mainConfigFile={0}'.format(main_config),
            'name={0}'.format(main),
            'paths.requireLib={0}'.format(almond_path),
            'include=requireLib',
        ]

        if not minify:
            cmd.append('optimize=none')

        # Add RequireJS paths for theme
        for dir_ref, dir in self.theme.keyed_static_dirs:
            dir = os.path.join(dir, 'js')
            log.debug("path _%s -> %s", key, dir)
            cmd.append('paths.{}={}'.format(dir_ref, dir))

        with self.tempfile() as (fd, temp_name):
            cmd.append('out={0}'.format(temp_name))
            self.run_command(cmd)
            file_path = self.write_from_file(key, temp_name, entry_point,
                                             output_dir)

        return file_path

    def tag_development(self, url):
        """
        Return an HTML fragment to use a require.js entry point in development.
        """
        return ''.join([
            js_preamble,
            HTML.script(src=self.theme.require_config_path),
            render_js_paths(self.theme),
            HTML.script(src=self.theme.require_path),
            HTML.script(src=url),
        ])

    def tag_production(self, url):
        """
        Return an HTML fragment to use a require.js entry point in production.
        """
        # FIXME Include the js preamble in the minified file itself, so it
        # doesn't have to be added to each tag fragment.
        return ''.join([
            js_preamble,
            HTML.script(src=url),
        ])
