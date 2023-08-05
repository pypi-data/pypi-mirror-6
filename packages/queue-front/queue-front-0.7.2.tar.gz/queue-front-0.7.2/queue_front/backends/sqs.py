"""
Backend for Amazon's Simple Queue Service.

This backend requires that the boto library is installed.
"""

from queue_front.backends.base import BaseQueue
from queue_front import InvalidBackend, QueueException, GETSETTING

try:
    from boto.sqs import connect_to_region
    from boto.sqs.message import Message
    from boto.exception import SQSError
except ImportError:
    raise InvalidBackend("Unable to import boto.")

REGION = GETSETTING('AWS_REGION', None)
KEY = GETSETTING('AWS_ACCESS_KEY_ID', None)
SECRET = GETSETTING('AWS_SECRET_ACCESS_KEY', None)

if not REGION:
    raise InvalidBackend("AWS_REGION not set.")
if not KEY:
    raise InvalidBackend("AWS_ACCESS_KEY_ID not set.")
if not SECRET:
    raise InvalidBackend("AWS_SECRET_ACCESS_KEY not set.")

CONN = connect_to_region(REGION, aws_access_key_id=KEY,
    aws_secret_access_key=SECRET)

class Queue(BaseQueue):
    '''sqs queue backend'''
    def __init__(self, name):
        self.name = name
        self.backend = 'sqs'
        self._connection = CONN
        # will either create a new queue or fetch an old one
        self._queue = self._connection.create_queue(name)

    def read_many(self, amount, block=False):
        '''Read many objects off the queue.'''
        if block:
            raise NotImplementedError('SQS cannot perform a blocking read.')
        try:
            # not guaranteed to get amount number of messages
            # even if you expect there to be that amount
            messes = self._queue.get_messages(amount)
            for i in range(len(messes)):
                mess = messes[i]
                if mess is not None:
                    self._queue.delete_message(mess)
                    messes[i] = mess.get_body()
            return messes
        except SQSError as err:
            raise QueueException(err).code

    def write(self, message):
        '''Write one object to the queue.'''
        try:
            mess = Message()
            mess.set_body(message)
            return self._queue.write(mess)
        except SQSError as err:
            raise QueueException(err).code

    def write_many(self, *messages):
        '''Write many objects to the queue.'''
        raise NotImplementedError

    def __len__(self):
        '''The number of objects in the queue.'''
        try:
            length = self._queue.count()
            if not length:
                length = 0
            return int(length)
        except SQSError as err:
            raise QueueException(err).code

    def __repr__(self):
        return "<Queue %s>" % self.name

def delete_queue(name):
    """
    Deletes a queue and any messages in it.
    """
    try:
        return CONN.delete_queue(CONN.create_queue(name))
    except SQSError as err:
        raise QueueException(err).code

def get_list():
    """
    Get a list of names for all queues.
    Returns a list of ``queue_front.backends.sqs.Queue`` objects.
    """
    return CONN.get_all_queues()
