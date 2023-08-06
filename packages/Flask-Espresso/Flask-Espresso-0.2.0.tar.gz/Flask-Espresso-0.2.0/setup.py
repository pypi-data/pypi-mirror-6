# -*- encoding: utf-8 -*-
"""
Flask-Espresso
==============

Adds Coffeescript [0] support to Flask [1] applications.

Flask-Espresso will compile on the fly your coffee-scripts in the template
directory of your application. To avoid performance issues, a cache mechanism
retrieves the scripts already compiled.


Install it
----------

    $ pip install Flask-Espresso

Note : Flask-Espresso requires you to have a javascript runtime installed on
       your system.

How-to use it
-------------

A simple example to show you how to use it. Create a new Flask application and
put a coffeescript file ``script.coffee`` in its template directory.

    from flask import Flask
    from flask.ext.espresso import Espresso, espresso

    app = Flask(__name__)
    esp = Espresso(app)

    @app.route("/")
    def hello():
        return espresso('script.coffee')

    if __name__ == "__main__":
        app.run(debug=True)

Links
-----

[0] http://www.coffeescript.org
[1] http://flask.pocoo.org/
"""


from setuptools import setup


setup(
    name='Flask-Espresso',
    version='0.2.0',
    url='https://github.com/morgan-del/flask-espresso',
    license='BSD',
    author='Morgan Delahaye-Prat',
    author_email='mdp@m-del.net',
    description='Adds Coffescript support to Flask applications',
    long_description=__doc__,
    packages=['flask_espresso'],
    package_dir={'flask_espresso': 'flask_espresso'},
    package_data={
        'flask_espresso': ['coffee-script.js'],
    },
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
        'PyExecJS',
        'slimit'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)