About
-----
Extension for configuring Flask from environment variables.

Requirements
------------
 * Flask

Installation
------------

::

    pip install flask-envconfig

Usage
-----
Simple usage:

::

    from flask import Flask
    from flask.ext.environ import EnvConfig

    app = Flask(__name__)
    env = EnvConfig(app)

Or, for the application factory pattern:

::

    env = EnvConfig()
    # At a later time
    env.init_app(app)

Now set your configuration variables in your shell, .env file or whatever:

::

    FLASK_DEBUG=True
    FLASK_SECRET_KEY="Something_or_the_other"

By default only environments variables prefixed with FLASK_ are processed and added to app.config. The extension strips off the prefix so FLASK_DEBUG becomes app.config['DEBUG'] and so forth.
The extension understands "True" to mean True, "False" to mean False and "None" to mean None.

The prefix can be changed if so desired:

::

    EnvConfig(app, 'MYPREFIX_')

Or

::

    env = EnvConfig()
    env.init_app(app, 'MYPREFIX_')
