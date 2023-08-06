from wdb.ext import WdbMiddleware
from paste.deploy.converters import asbool
from types import MethodType


def add_wdb_middleware(self, global_conf, app):
    if asbool(global_conf.get('debug')):
        app = WdbMiddleware(app)

    return app


def enable_wdb(app_config):
    object.__setattr__(app_config, 'add_debugger_middleware', MethodType(add_wdb_middleware, app_config, app_config.__class__))
