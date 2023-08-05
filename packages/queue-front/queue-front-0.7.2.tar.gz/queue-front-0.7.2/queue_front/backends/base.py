"Base queue class"

# Things to think about:
# - timeout/visibility timeout (boto)

class BaseQueue(object):
    """
    Abstract base class for queue backends.
    """
    def read(self, block=False):
        '''Read one object off the queue.'''
        return self.read_many(1, block=block)[0]

    def read_many(self, amount, block=False):
        '''Read many objects off the queue.'''
        raise NotImplementedError

    def write(self, message):
        '''Write one object to the queue.'''
        return self.write_many(message)[0]

    def write_many(self, *messages):
        '''Write many objects to the queue.'''
        raise NotImplementedError

    def __len__(self):
        '''The number of objects in the queue.'''
        raise NotImplementedError

def delete_queue(name):
    '''Delete a queue.'''
    raise NotImplementedError

def get_list():
    '''Get a list of all of the queues.'''
    raise NotImplementedError
