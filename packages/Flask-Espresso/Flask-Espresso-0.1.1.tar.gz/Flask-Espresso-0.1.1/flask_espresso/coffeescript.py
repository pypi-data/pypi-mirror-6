# -*- encoding: utf-8 -*-
"""
    flask.ext.espresso.coffeescript
    -------------------------------

    :copyright: (c) 2013 by Morgan Delahaye-Prat.
    :license: BSD, see LICENSE for more details.
"""


from __future__ import absolute_import
from __future__ import unicode_literals

import flask, execjs, io, os



def get_compiler():

    compiler = flask.current_app.config['ESPRESSO_DEFAULT_COMPILER']
    if compiler is None:
        compiler = os.path.join(os.path.dirname(__file__), 'coffee-script.js')
    with io.open(compiler, encoding='utf-8') as fp:
        return fp.read()

def compile_cs(script):
    """
    """
    runtime = execjs.get()
    compiler = get_compiler()
    ctx = runtime.compile(compiler)
    return ctx.call('CoffeeScript.compile', script)