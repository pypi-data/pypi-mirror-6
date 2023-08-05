# encoding: utf-8

from redis import StrictRedis
from redis.exceptions import RedisError
from datetime import datetime
import sys
import warnings


class Singleton(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance


class EventTracker(Singleton):
    _redis = None
    _log_file_name = None

    def __init__(self, redis=None, host='localhost', port=6379, db=0, log=None):
        self.set_connection_to_redis( redis or self.get_connection_to_redis(host=host, port=port, db=db))
        self._log_file_name = log


    @staticmethod
    def get_connection_to_redis(**kwargs):
        return StrictRedis(**kwargs)


    def set_connection_to_redis(self, redis):
        self._redis = redis


    def track_event(self, event_hash_name):
        date = datetime.now().date()
        try:
            if not self._redis.sismember('dates', date):
                self._redis.sadd('dates', date)
            self._redis.hincrby(event_hash_name, date, 1)

        except RedisError as e:
            warnings.warn( unicode(e))
            self.write_to_log(u'%s: %s: %s\n' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), unicode(e), event_hash_name))


    def write_to_log(self, message):
        try:
            f = open( self._log_file_name, 'at') if self._log_file_name else sys.stderr
            f.write( message)
            if self._log_file_name:
                f.close()

        except Exception as e:
            warnings.warn( unicode(e))

