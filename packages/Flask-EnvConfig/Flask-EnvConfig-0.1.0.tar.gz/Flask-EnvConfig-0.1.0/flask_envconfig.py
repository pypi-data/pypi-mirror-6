# -*- coding: utf-8 -*-
from __future__ import absolute_import
from os import environ

DEFAULT_ENV_PREFIX = 'FLASK_'


class EnvConfig(object):
    """Configure Flask from environment variables."""

    def __init__(self, app=None, prefix=DEFAULT_ENV_PREFIX):
        self.app = app
        if app is not None:
            self.init_app(app, prefix)

    def init_app(self, app, prefix=DEFAULT_ENV_PREFIX):
        for key, value in environ.iteritems():
            if key.startswith(prefix):
                key = key[len(prefix):]
                if value.lower() == 'true':
                    app.config[key] = True
                elif value.lower() == 'false':
                    app.config[key] = False
                elif value.lower() == 'none':
                    app.config[key] = None
                else:
                    try:
                        app.config[key] = value
                        app.config[key] = float(value)
                        app.config[key] = int(value)
                    except ValueError:
                        pass
