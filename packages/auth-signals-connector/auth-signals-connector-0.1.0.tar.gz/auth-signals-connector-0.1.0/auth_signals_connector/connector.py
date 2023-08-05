import logging

from django.conf import settings
from django.contrib.auth import signals


LOG = logging.getLogger(__name__)


def login_user(sender, request, user, **kwargs):
    LOG.info('User "{0}" logged in'.format(user))


def logout_user(sender, request, user, **kwargs):
    LOG.info('User "{0}" logged out'.format(user))


def login_failed(sender, credentials, **kwargs):
    LOG.info('Login failed: {0}'.format(credentials))


def configure_defaults():
    signals.user_logged_in.connect(login_user)
    signals.user_logged_out.connect(logout_user)
    signals.user_login_failed.connect(login_failed)


auth_signals = getattr(settings, 'AUTH_SIGNALS', None)

if auth_signals:
    if 'use_defaults' in auth_signals and auth_signals['use_defaults']:
        configure_defaults()
    if 'on_logged_in' in auth_signals:
        signals.user_logged_in.connect(auth_signals['on_logged_in'])
    if 'on_logged_out' in auth_signals:
        signals.user_logged_out.connect(auth_signals['on_logged_out'])
    if 'on_login_failed' in auth_signals:
        signals.user_login_failed.connect(auth_signals['on_login_failed'])
else:
    configure_defaults()
