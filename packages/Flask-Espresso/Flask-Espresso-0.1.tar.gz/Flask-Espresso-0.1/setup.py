# -*- encoding: utf-8 -*-
"""
Flask-Espresso
--------------

Adds `Coffescript`_ support to Flask applications.

.. _Coffeescript: http://coffeescript.org/

"""
from setuptools import setup


setup(
    name='Flask-Espresso',
    version='0.1',
    url='https://github.com/morgan-del/flask-espresso',
    license='BSD',
    author='Morgan Delahaye-Prat',
    author_email='mdp@m-del.net',
    description='Adds Coffescript support to Flask applications',
    long_description=__doc__,
    packages=['flask_espresso'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
        'PyExecJS'
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