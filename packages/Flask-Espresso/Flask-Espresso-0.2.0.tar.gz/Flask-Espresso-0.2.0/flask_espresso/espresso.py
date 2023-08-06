# -*- encoding: utf-8 -*-
"""
    flask.ext.espresso
    ------------------

    :copyright: (c) 2013 by Morgan Delahaye-Prat.
    :license: BSD, see LICENSE for more details.
"""


from __future__ import absolute_import
from __future__ import unicode_literals

import flask_espresso.coffeescript

import slimit
import execjs
import flask
import zlib


class Espresso(object):
    """
    Central controller class that can be used to configure how Flask-Espresso
    behaves. Each application that wants to use Flask-Espresso has to create,
    or run :meth:`init_app` on, an instance of this class after the
    configuration whas initialized.

    There are two usage modes which work very similar. One is binding the
    instance to a very Flask application::

        app = Flask(__name__)
        e = Espresso(app)

    The other possibility is to create the object once and configure the
    application later to support it::

        e = Espresso(app)

        def create_app():
            app = Flask(__name__)
            e.init_app(app)
            return app

    :param app: A Flask application.
    :param compiler: An alternate Coffeescript compiler to use.
    """

    cache = {}  # A class level dict acting as a cache.

    def __init__(self, app=None, compiler=None):

        self.app = app
        self._compiler = compiler

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Set up this instance for use with ``app``, if no app was passed to the
        constructor.

        :param app: A Flask application.
        """
        self.app = app
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['espresso'] = self

        app.config.setdefault('ESPRESSO_DEFAULT_COMPILER', self._compiler)

        # hot patching the spidermonkey hard-coded encoding.
        app.config.setdefault('ESPRESSO_SPIDERMONKEY_ENCODING', 'utf8')
        execjs._runtimes['SpiderMonkey']._encoding = app.config['ESPRESSO_SPIDERMONKEY_ENCODING']

    def clear_cache(self):
        """
        """
        Espresso.cache.clear()


def compute_key(value):
    """
    Computes a key for a ``value``.
    """
    # The CRC32 checksum is used because of the low security risk. If you
    # intend to compile CS from the outside world or a large number of
    # files, you should consider patching this method to use a stronger
    # hashing algorithm.
    return zlib.crc32(bytes(value.encode('utf-8')))


def from_cache(key, minified):
    """
    """
    return Espresso.cache.get((key, minified), None)


def to_cache(key, minified, value):
    """
    """
    Espresso.cache[key, minified] = value


def espresso(cs, force=False, cache=True, minify=False):
    """
    Returns a real response object that is an instance of
    """
    cs = flask.render_template(cs)
    key = compute_key(cs)

    resp = None
    if not force:
        resp = from_cache(key, minify)

    if resp is None:
        resp = flask_espresso.coffeescript.compile_cs(cs)
        if minify:
            resp = slimit.minify(resp, mangle=True, mangle_toplevel=True)
        if cache:                  # the caching only happen if the
            to_cache(key, minify, resp)    # file is compiled.

    return flask.Response(resp, mimetype='application/javascript')