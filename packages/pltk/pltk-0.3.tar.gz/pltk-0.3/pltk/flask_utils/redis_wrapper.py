"""Module for Redis operations. Holds the Redis Flask wrapper."""
import redis
import json


class Redis(redis.Redis):
    """
    Redis Flask wrapper, inspired by: https://github.com/satori/flask-redis

    Can also provide Flask configuration values using regular cache paradigm.
    Use Redis.get_config() to retreive any flask configuration value.
    This class will return the value stored in redis or if it is not (yet)
    stored, retreive it from the Flask config and store it for further use.
    This allows config changes at runtime.
    """

    def __init__(self, app):
        app.config.setdefault('REDIS_HOST', 'localhost')
        app.config.setdefault('REDIS_PORT', 6379)
        app.config.setdefault('REDIS_DB', 0)
        app.config.setdefault('REDIS_PASSWORD', None)
        app.config.setdefault('REDIS_CONFIG_KEY_PREFIX', 'CONFIG')

        self.app = app
        self.config_key_prefix = app.config['REDIS_CONFIG_KEY_PREFIX']

        super(Redis, self).__init__(
            host=app.config['REDIS_HOST'],
            port=app.config['REDIS_PORT'],
            db=app.config['REDIS_DB'],
            password=app.config['REDIS_PASSWORD'])

    def set_config(self, name, value):
        """Sets the config value spcified by name"""
        self.set('%s_%s' % (self.config_key_prefix, name), json.dumps(value))

    def get_config(self, name):
        """
        Returns a config value or app.config[name] if not found.
        Also, if the value is not found it is stored from app.config
        to make sure it will be retreived from redis the next time.
        """
        result = self.get('%s_%s' % (self.config_key_prefix, name))
        if result is None:
            result = self.app.config[name]
            self.set_config(name, result)
        else:
            result = json.loads(result)
        return result

    def erase_config(self):
        """
        Removes all config values stored in Redis
        effectively forcing a reload from the config stored in the
        settings .py file

        .. warning: This method uses KEYS with a pattern to determine
                    all the config values. The pattern used is::

                       "REDIS_CONFIG_KEY_PREFIX*"

                    where REDIS_CONFIG_KEY_PREFIX equals::

                       flask_app.config['REDIS_CONFIG_KEY_PREFIX']

                    Be sure this prefix is not used at any other place!
        """
        keys = self.keys('%s*' % self.config_key_prefix)
        if not keys:
            return
        for k in keys:
            self.delete(k)
