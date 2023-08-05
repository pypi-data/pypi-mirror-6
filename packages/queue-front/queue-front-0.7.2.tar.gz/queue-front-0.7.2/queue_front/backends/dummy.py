"""
A dummy queue that uses Python's built-in Queue class.

Useful for testing but likely not much else.
"""
try:
    import queue
except ImportError:
    import Queue as queue
from queue_front import QueueException
from queue_front.backends.base import BaseQueue

QUEUES = {}

def get_queue(name):
    '''Get a queue by name'''
    if name not in QUEUES:
        QUEUES[name] = queue.Queue()
    return QUEUES[name]

class Queue(BaseQueue):
    '''A dummy queue backend'''
    def __init__(self, name='default'):
        self.queue = get_queue(name)
        self.backend = 'dummy'
        self.name = name

    def read(self, block=False, timeout=None):
        '''Read one object off the queue. With a timeout.'''
        return self.read_many(1, block=block, timeout=timeout)[0]

    def read_many(self, amount, block=False, timeout=None):
        '''Read many objects off the queue.'''
        try:
            amt = amount
            messages = []
            while amt > 0:
                messages.append(self.queue.get(block=block, timeout=timeout))
                self.queue.task_done()
                amt -= 1
            return messages
        except queue.Empty as err:
            raise QueueException(err)

    def write(self, message):
        '''Write one object to the queue.'''
        return self.write_many(message)[0]

    def write_many(self, *messages):
        '''Write many objects to the queue.'''
        try:
            for message in messages:
                self.queue.put(message)
            return [True]*len(messages)
        except queue.Full as err:
            raise QueueException(err)

    def __len__(self):
        '''The number of objects in the queue.'''
        return self.queue.qsize()

    def __repr__(self):
        return "<Queue %s>" % self.name

def delete_queue(name):
    """Just start afresh."""
    try:
        del QUEUES[name]
        return True
    except KeyError:
        pass

def get_list():
    '''Get a list of all of the queues.'''
    return list(QUEUES)
