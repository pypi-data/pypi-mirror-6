from __future__ import absolute_import, print_function, division

import os.path
import subprocess
from mock import patch
from unittest import TestCase
from six import StringIO

from .. import compile
from ..assets.compiler import Compiler
from ..assets.less import LessCompiler
from ..assets.requirejs import RequireJSCompiler

from . import utils
from .example import foo


class TestCompileCommand(TestCase):

    def test_pcompile_usage(self):
        args = [
            'pcompile',
        ]
        buf = StringIO()
        with patch('sys.stderr', buf):
            with self.assertRaises(SystemExit) as cm:
                compile.main(args)
            exit_exception = cm.exception
            self.assertEqual(exit_exception.code, 2)
        self.assertIn('config_uri', buf.getvalue())

    def test_pcompile(self):
        args = ['pcompile', utils.test_ini_path]
        retcode = compile.main(args)
        self.assertEqual(retcode, 0)

    def test_pcompile_no_minify(self):
        args = ['pcompile', utils.test_ini_path, '--no-minify']
        retcode = compile.main(args)
        self.assertEqual(retcode, 0)
        # XXX Try to assett hat this makes longer assets or something.


class TestCompiler(TestCase):
    def setUp(self):
        self.theme = foo.FooTheme({})
        self.output_dir = os.path.join(utils.work_dir, 'compile-tests')

    def test_bad_shell(self):
        compiler = Compiler(None)
        buf = StringIO()
        with patch('sys.stdout', buf):
            with self.assertRaises(subprocess.CalledProcessError):
                argv = [
                    'false',
                ]
                compiler.run_command(argv)
        # XXX Try to test that this actually prints the stdout output of a
        # failed comamnd.

    def test_less_compile(self):
        compiler = LessCompiler(self.theme)
        path = compiler.compile('main-less', '/_foo/css/main.less',
                                self.output_dir)
        f = open(path, 'rb')
        buf_minified = f.read()
        self.assertGreater(len(buf_minified), 0)

        # Test that minified version is smaller than non-minified.
        compiler = LessCompiler(self.theme)
        path = compiler.compile('main-less', '/_foo/css/main.less',
                                self.output_dir, minify=False)
        f = open(path, 'rb')
        buf_unminified = f.read()

        self.assertLess(len(buf_minified), len(buf_unminified))

    def test_requirejs_compile(self):
        compiler = RequireJSCompiler(self.theme)
        path = compiler.compile('main-js', '/_foo/js/main.js', self.output_dir)
        f = open(path, 'rb')
        buf_minified = f.read()
        self.assertGreater(len(buf_minified), 0)

        # Test that minified version is smaller than non-minified.
        compiler = RequireJSCompiler(self.theme)
        path = compiler.compile('main-js', '/_foo/js/main.js', self.output_dir,
                                minify=False)
        f = open(path, 'rb')
        buf_unminified = f.read()

        self.assertLess(len(buf_minified), len(buf_unminified))
