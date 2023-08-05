from functools import wraps

try:  # Python 2.*
    from django.utils.encoding import force_unicode
except ImportError:  # Python 3.*
    from django.utils.encoding import force_text
    force_unicode = force_text
try:  # Django >= 1.4
    from django.utils import timezone
except ImportError:  # Django < 1.4
    from datetime import datetime
    timezone = datetime
from django.utils.importlib import import_module

from . import settings


def add_prefix(key):
    if settings.SESSION_REDIS_PREFIX:
        if not settings.SESSION_REDIS_PREFIX in str(key):
            return '%s:%s' % (
                settings.SESSION_REDIS_PREFIX,
                key
            )

    return key


def remove_prefix(key):
    if settings.SESSION_REDIS_PREFIX:
        key = str(key).replace(
            '%s:' % settings.SESSION_REDIS_PREFIX, '', 1
        )

    return key


def prefix(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        args = list(args)
        args[0] = add_prefix(args[0])
        return fn(*args, **kwargs)
    return wrapped


def import_by_path(dotted_path):
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)

        module = import_module(module_path)

        attr = getattr(module, class_name)
    except (ValueError, ImportError, AttributeError):
        raise ImportError('can not import %s' % dotted_path)

    return attr
