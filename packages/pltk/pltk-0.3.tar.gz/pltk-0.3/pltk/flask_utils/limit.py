"""Rate limit module insired by http://flask.pocoo.org/snippets/70/
Implements simple rate limiting decorator for views.

(Credits to Armin Ronacher <http://lucumr.pocoo.org/>).
"""

import time
from functools import update_wrapper
from flask import request, g


class RateLimit(object):
    """Rate limit abstraction.
    Implements simple counter with redis storage. Also stores important attributes used for rate limiting itself.
    """
    expiration_window = 10

    @property
    def remaining(self):
        """Get remaining number of requests available."""
        return self.limit - self.current

    @property
    def over_limit(self):
        """Check if number of requests is over limit."""
        return self.current >= self.limit

    def set_view_rate_limit(self):
        """Set current view's rate limit object."""
        g._view_rate_limit = self

    @classmethod
    def get_view_rate_limit(cls):
        """Get current view's rate limit object."""
        return getattr(g, '_view_rate_limit', None)

    def __init__(self, redis, key_prefix, limit, per, send_x_headers, expiration_window=None):
        """
        :param redis: redis wrapper object `redis.Redis` to use as storage.
        :param key_prefix: prefix to use for redis key-value storage `string`.
        :param limit: number of requests allowed `int`.
        :param per: amount of time (seconds) to limit number of requests above to `int`.
        :param send_x_headers: `bool` to send http headers X-RateLimit-* in response or not.
        :param expiration_window: amount of time (seconds) to expire current limit. `int`.
        """
        if expiration_window:
            self.expiration_window = expiration_window
        self.reset = (int(time.time()) // per) * per + per
        self.key = key_prefix + str(self.reset)
        self.limit = limit
        self.per = per
        self.send_x_headers = send_x_headers
        pipeline = redis.pipeline()
        pipeline.incr(self.key)
        pipeline.expireat(self.key, self.reset + self.expiration_window)
        self.current = min(pipeline.execute()[0], limit)


def on_limit_reached(limit):
    """Execute on rate limiting."""
    msg = ('Rate limit exceeded. You may not make more than %s '
           'requests per %s seconds on this call. Please wait %s seconds.')
    msg = msg % (
        str(limit.limit),
        str(limit.per),
        str(limit.expiration_window))
    return msg, 400


def rate(limit,
         per=300,
         send_x_headers=True,
         over_limit=on_limit_reached,
         scope_func=lambda: request.remote_addr,
         key_func=lambda: request.endpoint,
         ):
    """Rate limiting decorator for view functions.

    :param limit: number of requests allowed `int`.
    :param per: amount of time (seconds) to limit number of requests above to `int`.
    :param send_x_headers: `bool` to send http headers X-RateLimit-* in response or not.
    :param over_limit: callback function to handle over-limit situation.
    :param scope_func: callback function to get the 'scope' to form the storage key.
    :param key_func: callback function to get the 'key' to form the storage key.
    """
    def decorator(f):
        def rate_limited(*args, **kwargs):
            key = 'rate-limit/%s/%s/' % (key_func(), scope_func())
            rlimit = RateLimit(key, limit, per, send_x_headers)
            rlimit.set_view_rate_limit()
            if over_limit is not None and rlimit.over_limit:
                return over_limit(rlimit)
            return f(*args, **kwargs)
        return update_wrapper(rate_limited, f)
    return decorator


def inject_x_rate_headers(response):
    """Add limiting headers."""
    limit = RateLimit.get_view_rate_limit()
    if limit and limit.send_x_headers:
        h = response.headers
        h.add('X-RateLimit-Remaining', str(limit.remaining))
        h.add('X-RateLimit-Limit', str(limit.limit))
        h.add('X-RateLimit-Reset', str(limit.reset))
    return response
