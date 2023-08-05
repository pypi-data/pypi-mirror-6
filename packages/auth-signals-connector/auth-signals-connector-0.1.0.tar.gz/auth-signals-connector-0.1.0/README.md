django-auth-signals
===================

Simple abstraction layer for django.contrib.auth.signals <https://docs.djangoproject.com/en/dev/ref/contrib/auth/#module-django.contrib.auth.signals>.

Usage
-----
Add `auth_signals_connector` to `INSTALLED_APPS`:
```
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'auth_signals_connector'
)
```

By defaults, `auth_signals_connector` uses `auth_signals_connector.connector`
logger to log about 'login', 'logout' and 'login failed' actions.

You could change default behaviour in your `settings.py`:
```
AUTH_SIGNALS = {
    'use_defaults': True,
    'on_logged_in': some_login_func,
    'on_logged_out': some_logout_func,
    'on_login_failed': some_loginfail_func,
}
```

If `use_defaults` is `True`, default log handlers will be used too.
