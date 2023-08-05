from __future__ import absolute_import, print_function, division

import logging

import os
import tempfile
import time
import subprocess

from contextlib import contextmanager
from hashlib import sha1

log = logging.getLogger(__name__)


class Compiler(object):
    """
    Generic superclass for compilers of specific asset types. This class
    contains generic helper functions for compiling assets, and is subclassed
    to provide compilation functionality that is specific to certain asset
    types.
    """

    def __init__(self, theme):
        self.theme = theme

    def run_command(self, argv):
        """
        Run a shell command, and check the output.
        """
        log.debug('Running command: %s ...', ' '.join(argv))
        start_time = time.time()
        try:
            # FIXME Should this really be capturing stderr to stdout?
            subprocess.check_output(argv, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            log.error(e.output)
            raise
        elapsed_time = time.time() - start_time
        log.debug('Command completed in %0.4f seconds.', elapsed_time)

    def write(self, key, contents, entry_point, output_dir):
        """
        Write the compiled result for a particular entry point to the
        appropriate file and map file.
        """
        contents = contents.encode('utf-8')

        log.debug('Write - key: %r, entry_point: %r', key, entry_point)
        hash = sha1(contents).hexdigest()

        name = os.path.basename(entry_point)
        file_name = '{name}-{hash}.{ext}'.format(
            name=name, hash=hash, ext=self.name)
        file_path = os.path.join(output_dir, file_name)

        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)

        log.debug('Writing to %s ...', file_path)
        with open(file_path, 'wb') as f:
            f.write(contents)

        map_path = os.path.join(output_dir, key + '.map')
        log.debug('Writing map file to %s ...', map_path)
        with open(map_path, 'w') as f:
            f.write(file_name)

        return file_path

    def write_from_file(self, key, file_name, entry_point, output_dir):
        """
        Like ``write()``, but writes from a source file instead of a buffer
        variable.
        """
        with open(file_name) as f:
            contents = f.read()
        return self.write(key, contents, entry_point, output_dir)

    @contextmanager
    def tempfile(self, *args, **kwargs):
        """
        A context manager helper to generate a temporary file for quick use.
        """
        fd, name = tempfile.mkstemp(*args, **kwargs)
        try:
            yield fd, name
        finally:
            os.close(fd)
            os.remove(name)

    def tag(self, url, production=True):
        if production:
            return self.tag_production(url)
        else:
            return self.tag_development(url)
