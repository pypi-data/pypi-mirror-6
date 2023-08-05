''' the setup script'''
from os import path as os_path, environ as os_environ
from setuptools import setup, find_packages

UNSET = False
if os_environ.get('QUEUE_BACKEND', None) is None:
    UNSET = True
    os_environ['QUEUE_BACKEND'] = 'dummy'
import queue_front
if UNSET:
    del os_environ['QUEUE_BACKEND']

DESCRIPTION = LONG_DESCRIPTION = "A lowest-common-denominator API for interacting with lightweight queues. A fork of https://code.google.com/p/queues/."
if os_path.exists('README.rst'):
    LONG_DESCRIPTION = open('README.rst').read()

def read(fname):
    return open(os_path.join(os_path.dirname(__file__), fname)).read()

setup(
    name='queue-front',
    version=queue_front.VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Topic :: Utilities",
        "Framework :: Django",
    ],
    maintainer='Dwaiter.com',
    maintainer_email='dev@dwaiter.com',
    url='https://bitbucket.org/dwaiter/queue-front',
    packages=find_packages(),
    include_package_data=True,
    py_modules=['test'],
    package_dir={'queue_front': 'queue_front'},
)
