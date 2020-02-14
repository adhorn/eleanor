import time
import logging
from flask import request, g
from functools import update_wrapper
from eleanor.utils.api_utils import api_error_response
from eleanor.utils.redis import rs
try:
    from eleanor.settings import ENABLE_RATE_LIMIT
except ImportError:
    from eleanor.default_settings import ENABLE_RATE_LIMIT


class RateLimit(object):
    expiration_window = 10

    def __init__(self, key_prefix, limit, per, send_x_headers):
        self.reset = (int(time.time()) // per) * per + per
        self.key = key_prefix + str(self.reset)
        self.limit = limit
        self.per = per
        self.send_x_headers = send_x_headers
        p = rs.pipeline()
        p.incr(self.key)
        p.expireat(self.key, self.reset + self.expiration_window)
        try:
            self.current = min(p.execute()[0], limit)
        except Exception as exc:
            logging.warning(
                "RateLimiting function not working: {}".format(exc))
            return True
    remaining = property(lambda x: x.limit - x.current)
    over_limit = property(lambda x: x.current >= x.limit)


def get_view_rate_limit():
    return getattr(g, '_view_rate_limit', None)


def on_over_limit(limit):
    return api_error_response(
        code=429, message="Slow down!!")


def ratelimit(limit, per=300, send_x_headers=True,
              over_limit=on_over_limit,
              scope_func=lambda: request.remote_addr,
              key_func=lambda: request.endpoint):
    def decorator(f):
        def rate_limited(*args, **kwargs):
            key = 'rate-limit/%s/%s/' % (key_func(), scope_func())
            try:
                rlimit = RateLimit(key, limit, per, send_x_headers)
                g._view_rate_limit = rlimit
                if ENABLE_RATE_LIMIT:
                    if over_limit is not None and rlimit.over_limit:
                        return over_limit(rlimit)
                return f(*args, **kwargs)
            except Exception as exc:
                logging.debug(
                    "RateLimiting function not working: {}".format(exc))
                return f(*args, **kwargs)
        return update_wrapper(rate_limited, f)
    return decorator
