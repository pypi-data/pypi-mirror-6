"""
Backend for queues that implement the memcache protocol, including starling.

This backend requires either the pylibmc or bmemcached libraries to be
installed.
"""

from queue_front.backends.base import BaseQueue
from queue_front import InvalidBackend, QueueException, GETSETTING
import re

try:
    import pylibmc as memcache
except ImportError:
    import bmemcached as memcache
    memcache.Error = memcache.exceptions.MemcachedException
except:
    raise InvalidBackend("Unable to import a memcache library.")

CONN = GETSETTING('QUEUE_MEMCACHE_CONNECTION', None)

if not CONN:
    raise InvalidBackend("QUEUE_MEMCACHE_CONNECTION not set.")

class Queue(BaseQueue):
    '''memcache queue backend'''
    def __init__(self, name):
        self._connection = memcache.Client(CONN.split(';'))
        self.backend = 'memcached'
        self.name = name

    def read(self, block=False):
        '''Read one object off the queue.'''
        if block:
            raise NotImplementedError('Memcached cannot perform a blocking'
                ' read.')
        try:
            return self._connection.get(self.name)
        except (memcache.Error) as err:
            raise QueueException(err)

    def read_many(self, amount, block=False):
        '''Read many objects off the queue.'''
        raise NotImplementedError

    def write(self, message):
        '''Write one object to the queue.'''
        try:
            return self._connection.set(self.name, message, 0)
        except (memcache.Error) as err:
            raise QueueException(err)

    def write_many(self, *messages):
        '''Write many objects to the queue.'''
        raise NotImplementedError

    def __len__(self):
        '''The number of objects in the queue.'''
        try:
            return int(self._connection.get_stats()[0][1][
                'queue_{0}_items'.format(self.name)])
        except (memcache.Error) as err:
            raise QueueException(err)
        except AttributeError:
            # If this memcached backend doesn't support starling-style stats
            # or if this queue doesn't exist
            return 0

    def __repr__(self):
        return "<Queue %s>" % self.name

def delete_queue(name):
    """Memcached backends don't provide a way to do this."""
    raise NotImplementedError

def get_list():
    '''
        Get a list of all of the queues.
        Supports starling/peafowl-style queue_<name>_items introspection via
        stats.
    '''
    conn = memcache.Client(CONN.split(';'))
    queue_list = []
    queue_re = re.compile(r'queue\_(.*?)\_total_items')
    try:
        for server in conn.get_stats():
            for key in server[1].keys():
                all_ = queue_re.findall(key)
                if all_:
                    queue_list.append(all_[0])
    except (KeyError, AttributeError, memcache.Error):
        pass
    return queue_list
