from __future__ import absolute_import, print_function, division

from webhelpers2.html.tags import literal
from pyramid.settings import asbool

from .requirejs import RequireJSCompiler
from .less import LessCompiler


compiler_classes = {
    'requirejs': RequireJSCompiler,
    'less': LessCompiler,
}


def asset_tag(request, key, **kwargs):
    """
    Request method to render an HTML fragment containing tags which reference
    the supplied entry point. This will dispatch to the appropriate tag
    rendering function based on context and entry point type.
    """
    theme = request.theme
    assets = theme.stacked_assets
    url_path, asset_type = assets[key]
    settings = request.registry.settings
    should_compile = asbool(settings.get('pyramid_frontend.compile_%s' %
                                         asset_type))

    # FIXME Memoize compiler instances for this? Or maybe turn tag functions
    # into hybrid class/instance methods?
    cls = compiler_classes[asset_type]
    compiler = cls(theme)

    if should_compile:
        filename = theme.compiled_asset_path(key)
        url_path = '/compiled/' + theme.key + '/' + filename

    return literal(compiler.tag(url_path, production=should_compile))


def compile_asset(theme, output_dir, key, entry_point, asset_type, minify):
    cls = compiler_classes[asset_type]
    compiler = cls(theme)
    compiler.compile(key=key,
                     entry_point=entry_point,
                     output_dir=output_dir,
                     minify=minify)


def includeme(config):
    config.add_request_method(asset_tag, 'asset_tag')

    compiled_path = \
        config.registry.settings['pyramid_frontend.compiled_asset_dir']
    config.add_static_view(name='compiled', path=compiled_path)
