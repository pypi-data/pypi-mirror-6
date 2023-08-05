"""
Backend for beanstalkd queue.

This backend requires the beanstalkc library to be installed.
"""

from queue_front.backends.base import BaseQueue
from queue_front import InvalidBackend, QueueException, GETSETTING

try:
    import beanstalkc
except ImportError:
    raise InvalidBackend("Unable to import the beanstalkc library.")

CONN = GETSETTING('QUEUE_BEANSTALKD_CONNECTION', None)

if not CONN:
    raise InvalidBackend("QUEUE_BEANSTALKD_CONNECTION not set.")

try:
    HOST, PORT = CONN.split(':')
except ValueError:
    raise InvalidBackend("QUEUE_BEANSTALKD_CONNECTION should be in the format "
        "host:port (such as localhost:6379).")

try:
    PORT = int(PORT)
except ValueError:
    raise InvalidBackend("Port portion of QUEUE_BEANSTALKD_CONNECTION should be"
        " an integer.")

class Queue(BaseQueue):
    '''Benstalkd queue'''
    def __init__(self, name='default'):
        '''Setup the queue'''
        self._connection = beanstalkc.Connection(host=HOST, port=PORT)
        self.backend = 'beanstalkd'
        self.name = name
        self._connection.use(name)

    def read(self):
        '''Read one object off the queue. No blocking.'''
        try:
            job = self._connection.reserve()
            message = job.body
            job.delete()
            return message
        except (beanstalkc.DeadlineSoon, beanstalkc.CommandFailed,
            beanstalkc.UnexpectedResponse) as err:
            raise QueueException(err)

    def read_many(self, amount):
        '''Read many objects off the queue. No blocking.'''
        raise NotImplementedError

    def write(self, message):
        '''Write one object to the queue.'''
        try:
            return self._connection.put(message)
        except (beanstalkc.CommandFailed, beanstalkc.UnexpectedResponse) as err:
            raise QueueException(err)

    def __len__(self):
        '''The number of objects in the queue.'''
        try:
            return int(self._connection.stats().get('current-jobs-ready', 0))
        except (beanstalkc.CommandFailed, beanstalkc.UnexpectedResponse) as err:
            raise QueueException(err)

    def __repr__(self):
        '''str repr'''
        return "<Queue %s>" % self.name

def delete_queue(name):
    """Beanstalkd backends don't provide a way to do this."""
    raise NotImplementedError

def get_list():
    '''Get a list of all of the queues.'''
    return beanstalkc.Connection(host=HOST, port=PORT).tubes()
