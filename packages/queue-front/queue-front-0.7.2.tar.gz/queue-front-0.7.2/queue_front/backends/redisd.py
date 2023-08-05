"""
Backend for redis.
"""

from queue_front.backends.base import BaseQueue
from queue_front import InvalidBackend, QueueException, GETSETTING
import math

try:
    import redis
except ImportError:
    raise InvalidBackend("Unable to import redis.")

CONN = DB = None

CONN = GETSETTING('QUEUE_REDIS_CONNECTION', None)
DB = GETSETTING('QUEUE_REDIS_DB', None)
TIMEOUT = GETSETTING('QUEUE_REDIS_TIMEOUT', None)

if not CONN:
    raise InvalidBackend("QUEUE_REDIS_CONNECTION not set.")

try:
    HOST, PORT = CONN.split(':')
except ValueError:
    raise InvalidBackend("QUEUE_REDIS_CONNECTION should be in the format "
        "host:port (such as localhost:6379).")

try:
    PORT = int(PORT)
except ValueError:
    raise InvalidBackend("Port portion of QUEUE_REDIS_CONNECTION should be an "
        "integer.")


def _get_connection(host=HOST, port=PORT, db_uri=DB, timeout=TIMEOUT):
    ''' get the connection to the redis database'''
    kwargs = {'host' : host, 'port' : port}
    if DB:
        kwargs['db'] = db_uri
    if timeout:
        kwargs['socket_timeout'] = float(timeout)
    return redis.Redis(**kwargs)

CONN = _get_connection()

class Queue(BaseQueue):
    '''Redis queue backend'''
    def __init__(self, name):
        try:
            self.name = name
            self.backend = 'redis'
            self._connection = CONN
        except redis.RedisError as err:
            raise QueueException(err)

    def read_many(self, amount, block=False, timeout=0):
        '''Read many objects off the queue. With timeout.'''
        try:
            pipe = self._connection.pipeline()
            amt = amount
            while amt > 0:
                if block:
                    # Redis requires an integer, so round a float UP to the
                    # nearest int (0.1 -> 1).
                    try:
                        pipe.blpop(self.name,
                            timeout=int(math.ceil(timeout)))[1]
                    except TypeError:
                        pass
                else:
                    pipe.lpop(self.name)
                amt -= 1
            return pipe.execute()
        except redis.RedisError as err:
            raise QueueException(err)

    def write_many(self, *values):
        '''Write one object to the queue.'''
        try:
            pipe = self._connection.pipeline()
            for value in values:
                pipe.rpush(self.name, value)
            return pipe.execute()
        except redis.RedisError as err:
            raise QueueException(err)

    def __len__(self):
        '''The number of objects in the queue.'''
        try:
            return self._connection.llen(self.name)
        except redis.RedisError as err:
            raise QueueException(err)

    def __repr__(self):
        '''str repr'''
        return "<Queue %s>" % self.name

def delete_queue(name):
    """Delete a queue"""
    try:
        resp = CONN.delete(name)
        return bool(resp and resp == 1)
    except redis.RedisError as err:
        raise QueueException(err)

def get_list():
    '''Get a list of all of the queues.'''
    return CONN.keys('*')
