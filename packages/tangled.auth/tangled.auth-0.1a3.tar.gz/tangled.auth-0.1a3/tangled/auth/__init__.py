from webob.exc import HTTPForbidden, HTTPUnauthorized

from tangled.settings import parse_settings
from tangled.web.exc import ConfigurationError

from .authentication import *
from .authorization import *


def include(app):
    conversion_map = {
        'authenticator': 'object',
        'authorizer': 'object',
    }
    defaults = {
        'authorizer': None,
    }
    required = ('authenticator',)
    settings = parse_settings(
        app.settings, conversion_map=conversion_map, defaults=defaults,
        required=required, prefix='tangled.auth.')

    app['authenticator'] = settings['authenticator']
    app['authenticator.args'] = parse_settings(
        settings, prefix='authenticator.')

    app['authorizer'] = settings['authorizer']
    app['authorizer.args'] = parse_settings(settings, prefix='authorizer.')

    if app['authorizer'] and not app['authenticator']:
        raise ConfigurationError('No authenticator registered')

    app.settings['tangled.app.handler.auth'] = auth_handler
    app.add_config_field('*/*', 'requires_authentication', False)
    app.add_config_field('*/*', 'permission', None)
    app.add_config_field('*/*', 'not_logged_in', False)
    app.add_request_attribute(authenticator, reify=True)
    app.add_request_attribute(authorizer, reify=True)


def auth_handler(app, request, next_handler):
    info = request.resource_config

    if info.requires_authentication or info.permission:
        if not request.authenticator.user_id:
            raise HTTPUnauthorized()

    if info.not_logged_in:
        if request.authenticator.user_id:
            raise HTTPForbidden()

    if info.permission:
        if request.authorizer:
            user_id = request.authenticator.user_id
            if not request.authorizer.authorized(user_id, info.permission):
                raise HTTPForbidden()
        else:
            raise RuntimeError('No Authorizer configured')

    return next_handler(app, request)


# Request attributes

def authenticator(request):
    app = request.app
    args = app['authenticator.args']
    return app['authenticator'](app, request, **args)


def authorizer(request):
    app = request.app
    authorizer = app['authorizer']
    if authorizer:
        args = app['authorizer.args']
        return app['authorizer'](app, request, **args)
