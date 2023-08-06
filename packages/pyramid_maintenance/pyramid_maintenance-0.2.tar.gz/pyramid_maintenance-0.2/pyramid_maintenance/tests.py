import unittest

from pyramid.config import Configurator
from pyramid.security import Everyone, Allow
from pyramid.view import view_config
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from webtest import TestApp


def stupid_callback(uid, *args, **kw):
    """Simple callback"""
    return []


class RootFactory(object):
    """
        Simple RootFactory used for tests
    """
    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, 'permission:administor', 'admin'),
    ]

    def __init__(self, request):
        pass


@view_config(route_name='something', renderer='something.mako', permission='view')
def view_something(request):
    """A view of something"""
    return {}


class ViewTests(unittest.TestCase):

    def _get_app(self, settings):
        config = Configurator(settings=settings, root_factory=RootFactory)
        authorization_policy = ACLAuthorizationPolicy()
        config.set_authorization_policy(authorization_policy)
        authn_policy = AuthTktAuthenticationPolicy(
                    'sosecret', callback=stupid_callback, hashalg='sha512')
        config.set_authentication_policy(authn_policy)
        config.include('pyramid_mako')
        config.add_route('something', '/something')
        config.scan()
        app = TestApp(config.make_wsgi_app())
        return app


    def test_tween_maintenance(self):
        # Tween not yet enabled
        settings = {
            'mako.directories': 'pyramid_maintenance:tests/templates',
        }
        app = self._get_app(settings)
        content = app.get('/something')
        self.assertTrue('This is something' in content)

        # With tween enabled
        settings = {
            'mako.directories': 'pyramid_maintenance:tests/templates',
            'pyramid.tweens': 'pyramid_maintenance.tween_maintenance',
            'pyramid_maintenance.permissions': 'admin',
            'pyramid_maintenance.template': 'maintenance.mako',
        }
        app = self._get_app(settings)
        content = app.get('/something')
        self.assertTrue('Maintenance page' in content)

        # With tween enabled, allow to by-pass maintenance
        settings = {
            'mako.directories': 'pyramid_maintenance:tests/templates',
            'pyramid.tweens': 'pyramid_maintenance.tween_maintenance',
            'pyramid_maintenance.permissions': 'view',
            'pyramid_maintenance.template': 'maintenance.mako',
        }
        app = self._get_app(settings)
        content = app.get('/something')
        self.assertTrue('This is something' in content)

        # With tween enabled, allow to by-pass maintenance, several permissions in different forms
        settings = {
            'mako.directories': 'pyramid_maintenance:tests/templates',
            'pyramid.tweens': 'pyramid_maintenance.tween_maintenance',
            'pyramid_maintenance.permissions': 'admin\r\n view , ',
            'pyramid_maintenance.template': 'maintenance.mako',
        }
        app = self._get_app(settings)
        content = app.get('/something')
        self.assertTrue('This is something' in content)
