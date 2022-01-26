"""Utilities."""
# -- XXX This module must not use translation as that causes
# -- a recursive loader import!

import importlib

from django.conf import settings
from django.utils import timezone

# see Issue celery/django-celery#222
now_localtime = getattr(timezone, 'template_localtime', timezone.localtime)


def now():
    """Return the current date and time."""
    if getattr(settings, 'USE_TZ', False):
        return now_localtime(timezone.now())
    else:
        return timezone.now()


def raw_delete(queryset):
    """Raw delete given queryset."""
    return queryset._raw_delete(queryset.db)


def get_celery_app():
    module_path, app_attr = settings.CELERY_APP_MODULE.rsplit('.', maxsplit=1)
    celery_module = importlib.import_module(module_path)
    return getattr(celery_module, app_attr)
