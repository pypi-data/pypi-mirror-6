Flask-Soy
=========

Flask-Soy is an extension to Flask that adds support for rendering
Closure Templates (Soy). It follows the standard Flask conventions
for working with the built-in Jinja templates.

Why to Use Soy Templates?
-------------------------

The main advantage of Soy templates is that you can use the same
templates on both server and client side, because they can be
compiled to both Python and JavaScript.

Installation
------------

First you need to install the Soy Python package. Download `closure-templates-for-python-latest.zip <https://bitbucket.org/lalinsky/closure-templates/downloads/closure-templates-for-python-latest.zip>`_
and unzip it in a temporary directory. Inside the directory run the
following command to install the Python package::

    $ python setup.py install

There is also the Soy-to-Python compiler jar file, which you need to
copy to some convenient location (e.g. your project directory).

In order to be able to compile Soy templates, you will also need to make sure
you have Java (JRE) version 6 or newer installed with the ``java`` executable
in your path. For using the templates from JavaScript you also need the
Soy-to-JavaScript compiler from `closure-templates-for-javascript-latest.zip <http://closure-templates.googlecode.com/files/closure-templates-for-javascript-latest.zip>`_

After that you can install Flask-Soy using pip::

    $ pip install Flask-Soy

Usage
-----

Template Rendering
``````````````````

To get started all you need to do is to instanciate a ``Soy`` object after
configuring the application and use the ``render_template`` function::

    from flask import Flask
    from flask.ext.soy import Soy, render_template

    app = Flask(__name__)
    soy = Soy(app)

    @app.route('/')
    def index():
        return render_template('myapp.index', name='tofu')

Flask-Soy will automatically compile templates from the standard Flask
directories, so in order to get the Python code above work, you could
have a template like this in ``templates/pages.soy``::

    {namespace myapp}
    
    /**
     * Renders the index page.
     * @param name
     */
    {template .index}
      Hello {$name}!
    {/template}

Client-side Template Rendering
``````````````````````````````

The main advantage of Soy templates is that you can use them both from Python and JavaScript.
If you define a view like this, you can access the JavaScript version of the templates on
the URL ``/templates.js``::

    from flask.ext.soy import render_js_templates

    @app.route('/templates.js')
    def templates_js():
        return render_js_templates()

On the JavaScript side, you can then use the templates as simple functions, e.g.::

    <script src="/static/soyutils.js"></script>
    <script src="/templates.js"></script>
    <script>
        var html = myapp.index({name: "tofu"});
    </script>

See the `official documentation <https://developers.google.com/closure/templates/docs/javascript_usage>`_ for
more information on using Soy templates from JavaScript.

Integration with Flask-Script
`````````````````````````````

You can add a command to pre-compile Soy templates to your ``manage.py`` using
the following code::

    from flask.ext.script import Manager
    from flask.ext.soy import CompileSoyCommand

    manager = Manager(app)
    manager.add_command("compile_soy", CompileSoyCommand())

Configuration
`````````````

A list of configuration keys currently understood by the extension:

=====================  ==============================================================================
``SOY_COMPILER_PATH``  Path to a directory where the compiler .jar files are located.
``SOY_CACHE``          Where to save compiled Python code. By default, Python code is not cached.
``SOY_JS_CACHE``       Where to save compiled JavaScript code. By default, Python code is not cached.
=====================  ==============================================================================
