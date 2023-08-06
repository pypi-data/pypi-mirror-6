"""
    flask.ext.soy
    ~~~~~~~~~~~~~

    Provides support for Closure Templates (Soy) in Flask.

    :copyright: (c) 2014 by Lukas Lalinsky <lukas@oxygene.sk>
    :license: Apache 2.0, see COPYING for more details.
"""

import os
import tempfile
from contextlib import closing
from flask import current_app, make_response
from soy import SoyFileSet
from soy.tofu import SoyTofu


try:
    from flask.ext.script import Command
except ImportError:
    Command = object


class _SoyAppState(object):

    def __init__(self, app, soy):
        self.app = app
        self.soy = soy

        self.templates = list(self.find_templates())
        builder = SoyFileSet.Builder()
        for template in self.templates:
            builder.add(template)

        self.sfs = builder.build()
        self.tofu = None

    def find_template_dirs(self):
        yield os.path.join(self.app.root_path, self.app.template_folder)
        blueprints = getattr(self.app, 'blueprints', {})
        for blueprint in blueprints.itervalues():
            if blueprint.template_folder:
                yield os.path.join(blueprint.root_path, blueprint.template_folder)

    def find_templates(self):
        for path in self.find_template_dirs():
            if not os.path.isdir(path):
                continue
            for name in os.listdir(path):
                if name.endswith('.soy'):
                    yield os.path.join(path, name)

    def compile_templates(self, recompile=False):
        if self.tofu is None or recompile:
            with self._compile_py_templates() as file:
                self.tofu = SoyTofu.fromFile(file)
        return self.tofu

    def render_template(self, template, **context):
        tofu = self.compile_templates()
        self.app.update_template_context(context)
        return tofu.newRenderer(template).setData(**context).render()

    def render_js_templates(self):
        with self._compile_js_templates() as file:
            rv = make_response(file.read())
            rv.mimetype = 'text/javascript'
            return rv

    def _find_last_template_mtime(self):
        mtime = -1
        for template in self.templates:
            mtime = max(mtime, os.lstat(template).st_mtime)
        return mtime

    def _get_cache_path(self, option):
        file_name = self.app.config[option]
        if file_name:
            if not os.path.isabs(file_name):
                return os.path.join(self.app.root_path, file_name)
            return file_name

    def _check_cache(self, path):
        if os.path.exists(path):
            mtime = os.lstat(path).st_mtime
            if mtime > self._find_last_template_mtime():
                return True
        return False

    def _compile_templates(self, compiler, cache_key):
        cache_path = self._get_cache_path(cache_key)
        if cache_path:
            if not self._check_cache(cache_path):
                compiler(cache_path, self.app.config['SOY_COMPILER_PATH'])
            return open(cache_path, 'r')
        file = tempfile.NamedTemporaryFile()
        compiler(file.name, self.app.config['SOY_COMPILER_PATH'])
        return file

    def _compile_py_templates(self):
        return closing(self._compile_templates(self.sfs.compileToPyFile, 'SOY_CACHE'))

    def _compile_js_templates(self):
        return closing(self._compile_templates(self.sfs.compileToJsFile, 'SOY_JS_CACHE'))


class Soy(object):

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        state = _SoyAppState(app, self)

        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['soy'] = state

        app.config.setdefault('SOY_CACHE', None)
        app.config.setdefault('SOY_JS_CACHE', None)
        app.config.setdefault('SOY_COMPILER_PATH', None)

    def find_templates(self, app=None):
        if app is None:
            app = self.app
        return app.extensions['soy'].templates


def render_template(template, **context):
    return current_app.extensions['soy'].render_template(template, **context)


def render_js_templates():
    return current_app.extensions['soy'].render_js_templates()


class CompileSoyCommand(Command):
    """Compile Soy templates to Python and JavaScript files."""

    def get_options(self):
        return []

    def run(self):
        current_app.extensions['soy']._compile_py_templates()
        current_app.extensions['soy']._compile_js_templates()

