import redis

from . import settings, utils


def get_redis_server():
    if not settings.SESSION_REDIS_CONNECTION_POOL is None:
        return redis.StrictRedis(
            connection_pool=utils.import_by_path(
                settings.SESSION_REDIS_CONNECTION_POOL
            )
        )

    if not settings.SESSION_REDIS_URL is None:
        return redis.StrictRedis.from_url(
            settings.SESSION_REDIS_URL
        )

    if not settings.SESSION_REDIS_UNIX_DOMAIN_SOCKET_PATH is None:
        return redis.StrictRedis(
            unix_socket_path=settings.SESSION_REDIS_UNIX_DOMAIN_SOCKET_PATH,
            db=settings.SESSION_REDIS_DB,
            password=settings.SESSION_REDIS_PASSWORD
        )

    return redis.StrictRedis(
        host=settings.SESSION_REDIS_HOST,
        port=settings.SESSION_REDIS_PORT,
        db=settings.SESSION_REDIS_DB,
        password=settings.SESSION_REDIS_PASSWORD
    )


redis_server = get_redis_server()
