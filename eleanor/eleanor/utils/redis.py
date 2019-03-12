import redis


try:
    from eleanor.settings import REDIS_URL
except ImportError:
    from eleanor.default_settings import REDIS_URL


pool = redis.ConnectionPool(host=REDIS_URL, port=6379, db=0)
rs = redis.Redis(
    connection_pool=pool,
    socket_timeout=2,
    socket_connect_timeout=2
)


def info():
    return rs.info()


def ping():
    return rs.ping()


def flush_all():
    return rs.flushdb()


def get_key(key):
    return rs.get(key)


def set_key(key, value):
    return rs.set(key, value)


def remove_key(key):
    return rs.delete(key)

# Memcached interface support


def get_cache(key):
    return get_key(key)


def set_cache(key, value):
    return set_key(key, value)


def del_cache(key):
    return remove_key(key)

# end Memcached interface support
