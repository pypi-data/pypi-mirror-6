__author__ = 'tarzan'

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid_vgid_oauth2 import set_put_user_callback
from pyramid_backend.views import add_model_view


def get_roles_from_settings(settings):
    roles = settings.get('pyramid_backend_vgid_oauth2.roles', 'g.super_saiyan,g.admin')
    return filter(bool, map(lambda r: r.strip(), roles.split(',')))

from pyramid_backend_vgid_oauth2.adapters import sa

BackendUser = None


def includeme(config):
    """
    :type config: pyramid.config.Configurator
    :return:
    """
    global BackendUser
    settings = config.get_settings()

    if sa.initialize_from_settings(settings):
        adapter = sa
    else:
        return

    BackendUser = adapter.BackendUser
    set_put_user_callback(adapter.put_user_callback)
    auth_policy = AuthTktAuthenticationPolicy(
        secret=settings.get('pyramid_backend_vgid_oauth2.auth_secret', 'gyPsi-a<G:7ptRo*q%6e'),
        callback=adapter.get_user_callback_for_auth_policy,
    )
    config.set_authentication_policy(auth_policy)
    config.set_request_property(adapter.get_user_for_request, 'authenticated_user', reify=True)
    add_model_view(config, model=BackendUser)