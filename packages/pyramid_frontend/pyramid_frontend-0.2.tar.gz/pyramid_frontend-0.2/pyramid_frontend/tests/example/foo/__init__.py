from __future__ import absolute_import, print_function, division

from ..base import BaseTheme
from pyramid_frontend.images.chain import FilterChain


def foo_includeme(config):
    test_includes = config.registry.settings.setdefault('test_includes', [])
    test_includes.append('foo')


class FooTheme(BaseTheme):
    key = 'foo'
    image_filters = [
        FilterChain('tiny', width=64, height=64, crop=True),
    ]
    assets = {
        'main-less': ('/_foo/css/main.less', 'less'),
        'main-js': ('/_foo/js/main.js', 'requirejs'),
    }
    includes = [
        '.foo_includeme',
    ]
