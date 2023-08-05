# -*- coding: utf-8 -*-

import sys
import pkg_resources


class PathDictProxy(dict):
    _proxies = {}

    def __init__(self, *args, **kw):
        super(PathDictProxy, self).__init__(*args, **kw)
        self._proxies = {}

    def set_proxy(self, key, value):
        self[key] = value
        self._proxies[key] = value

    def __setitem__(self, key, value):
        if key in self._proxies:
            value = self._proxies[key] + value
        return super(PathDictProxy, self).__setitem__(key, value)


def setup_themes(app):
    theme_paths = []

    for plugin in pkg_resources.iter_entry_points('sphinx_themes'):
        try:
            m = plugin.load()
        except ImportError:
            msg = "warn: Can't import '" + plugin.module_name + "'\n"
            sys.stderr.write(msg)
            continue
        
        if callable(m):
            path = m()
        else:
            path = m
        theme_paths.append(path)

    if theme_paths:
        theme_paths.extend(app.config.html_theme_path)
        # sphinx/config.py (L201) manipulate config.__dict__ directory.
        # this is tricky hook for such implementation that
        # works only for sphinx-1.0.7, perhaps.
        app.config.__dict__ = PathDictProxy(app.config.__dict__)
        app.config.__dict__.set_proxy('html_theme_path', theme_paths)


def setup_directives(app):
    for plugin in pkg_resources.iter_entry_points('sphinx_directives'):
        try:
            module_setup = plugin.load()
        except ImportError:
            msg = "warn: Can't import '" + plugin.module_name + "'\n"
            sys.stderr.write(msg)
            continue
        
        module_setup(app)


def is_supported_theme_plugin_feature():
    import sphinx
    import re
    _m = re.match(r'([\d\.]+)(.*)', '1.2b3')
    if not _m:
        return False
    _version, _sub = _m.groups()
    return _version >= '1.2' and not(_version == '1.2' and _sub)


def setup(app):
    import warnings
    warnings.warn(
        "sphinxjp.themecore is deprecated. Please use Sphinx-1.2",
        DeprecationWarning)

    if not is_supported_theme_plugin_feature():
        setup_themes(app)
    setup_directives(app)
