# Queue Front #
A lowest-common-denominator API for interacting with lightweight queues. A fork of https://code.google.com/p/queues/. This main reason for this fork was to add python 3.0+ compatibility. Although you should be aware that the backend libraries may not be python 3.0+ compatible.

## Backends ##

* Amazon sqs

    * [boto](https://github.com/boto/boto), MIT

* memcached*

    * [pylibmc](http://sendapatch.se/projects/pylibmc/), 3-clause BSD (a python wrapper around [TangentOrg‘s](http://tangent.org/) [libmemcached](http://libmemcached.org/libMemcached.html) library.)
    * [bmemcached](https://github.com/jaysonsantos/python-binary-memcached), MIT (a pure python module)

* beanstalkd

    * [beanstalkc](http://github.com/earl/beanstalkc/tree/master), APL-2.0

* redis

    * [redis-py](https://github.com/andymccurdy/redis-py), MIT

*memcached backends must use a queueing server such as MemcacheQ.

## Example ##
    $ export QUEUE_BACKEND=redisd
    $ export QUEUE_REDIS_CONNECTION=localhost:6379
    $ python
    >>> from queue_front import queues
    >>> q = queues.Queue('myname')
    >>> q.write('test')
    True
    >>> len(q)
    1
    >>> q.read()
    test
    >>> queues.get_list()
    ['myname']

#Advanced

##Packages Security

This module, when packaged, is signed with the following key:

Mario Rosa's Key with id 0x8EBBFA6F (full fingerprint F261 96E4 8EF2 ED4A 26F8  58E9 04AA
48D1 8EBB FA6F) and his email is mario@dwaiter.com

You can find this key on servers like [pgp.mit.edu][PGP MIT].

[PGP MIT]: http://pgp.mit.edu
