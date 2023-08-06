Flask-Espresso
==============

Adds `Coffeescript <http://www.coffeescript.org>`_ support to Flask applications.

Flask-Espresso will compile on the fly your coffee-scripts in the template
directory of your application. To avoid performance issues, a cache mechanism
retrieves the scripts already compiled.


Install it
----------

::

    pip install Flask-Espresso

*Note : Flask-Espresso requires you to have a javascript runtime installed on your system.*

How-to use it
-------------

A simple example to show you how to use it. Create a new Flask application and put a coffeescript file ``script.coffee`` in its template directory. ::

    from flask import Flask
    from flask.ext.espresso import Espresso, espresso

    app = Flask(__name__)
    esp = Espresso(app)

    @app.route("/")
    def hello():
        return espresso('script.coffee')

    if __name__ == "__main__":
        app.run(debug=True)

Configuration
-------------

Application configuration
^^^^^^^^^^^^^^^^^^^^^^^^^
The following config options are available :

  ``ESPRESSO_DEFAULT_COMPILER`` : the full path to an alternate ``coffe-script.js`` in charge of
  the compilation of the scripts. If not set, Flask-Espresso will rely on the embedded version
  of coffee-script.

  ``ESPRESSO_SPIDERMONKEY_ENCODING`` : If you are using mozilla's spidermonkey as the javascript
  interpreter, it seems that the encoding can be hardcoded leading to some errors. This option lets
  you override it. (i.e : ``ESPRESSO_SPIDERMONKEY_ENCODING = 'latin1'``)

Espresso options
^^^^^^^^^^^^^^^^
When calling the ``espresso`` function, the following options are available  :

  ``force`` : Tell espresso to force the compilation of the file, despite having it in the cache.
  (default is ``False``)

  ``cache`` : Tell espresso to not cache the result of the compilation. (default is ``True``)

  ``minify`` : Tell espresso to minify the result of the compilation. (default is ``False``)

The following example show you how to use them::

   espresso('script.coffee', force=True, cache=False, minify=True)


