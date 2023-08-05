from django.contrib.sessions.backends.base import CreateError

from . import utils, connection


@utils.prefix
def expire(key):
    return connection.redis_server.ttl(key)


@utils.prefix
def keys(pattern):
    return connection.redis_server.keys(pattern)


@utils.prefix
def get(key):
    value = connection.redis_server.get(key)

    value = utils.force_unicode(value)

    return value


@utils.prefix
def exists(key):
    return connection.redis_server.exists(key)


@utils.prefix
def delete(key):
    return connection.redis_server.delete(key)


@utils.prefix
def save(key, expire, data, must_create):
    expire = int(expire)

    data = utils.force_unicode(data)

    if must_create:
        if connection.redis_server.setnx(key, data):
            connection.redis_server.expire(key, expire)
        else:
            raise CreateError
    else:
        connection.redis_server.setex(key, expire, data)
