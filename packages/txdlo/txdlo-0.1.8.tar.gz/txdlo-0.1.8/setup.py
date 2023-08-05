#!/usr/bin/env python

# The description below is an RST version of the beginning of README.md
# (I'm not a fan of RST, but PyPI knows how to display it.)

description = """\
txdlo - a (Twisted) deferred list observer
==========================================

``txdlo`` is a Python package that provides a class called
``DeferredListObserver``.

As you might guess, ``DeferredListObserver`` lets you observe callback and
errback events from a list of `Twisted <http://twistedmatrix.com>`_
`deferreds
<http://twistedmatrix.com/documents/current/core/howto/defer.html>`_.  You
can add observers that will be passed information about deferreds firing.
You can add deferreds to the observed list at any time, which is very
useful if you're dynamically creating deferreds that you want to monitor.

The class can be used to easily build functions or classes that provide
deferreds that fire when arbitrary combinations of events from the observed
deferreds have occurred.

For example you can write functions or classes that support deferreds that

* Implement Twisted's ``DeferredList`` or simple variants of it, or that let
  you separate the various behaviors of ``DeferredList`` into simpler
  functions.
* Provide a deferred that fires when N of the observed deferreds have fired.
* Provide a deferred that ignores errors until one of the observed deferred
  succeeds, only firing with an error if all the observed deferreds fail.
* Or (a more involved example), suppose you have 3 methods that can return
  you a user's avatar: a fast local cache, a filesystem, and a slow network
  call to Gravatar. You want to write a deferred-returning function that
  launches all three lookups at once and fires its deferred with the first
  answer. But if the cache and/or filesystems fails first, you don't want
  to trigger an error, you instead want to take the result from Gravatar
  and add it to the cache and/or filesystem, as well firing the returned
  deferred with the result (wherever it comes from). Only if all three
  lookups fail do you want to errback the deferred you returned.

The source for ``txdlo`` lives at `https://github.com/terrycojones/txdlo
<https://github.com/terrycojones/txdlo>`_.

"""

d = dict(name='txdlo',
         version='0.1.8',
         provides=['txdlo'],
         maintainer='Terry Jones',
         maintainer_email='terry@jon.es',
         url='https://github.com/terrycojones/txdlo',
         download_url='https://github.com/terrycojones/txdlo',
         packages=['txdlo'],
         include_package_data=True,
         keywords=['twisted deferred observer'],
         classifiers=[
             'Programming Language :: Python',
             'Framework :: Twisted',
             'Development Status :: 4 - Beta',
             'Intended Audience :: Developers',
             'License :: OSI Approved :: Apache Software License',
             'Operating System :: OS Independent',
             'Topic :: Software Development :: Libraries :: Python Modules',
         ],
         description='A Twisted class for observing a set of deferreds.',
         long_description=description)

try:
    from setuptools import setup
    _ = setup  # Keeps pyflakes from complaining.
except ImportError:
    from distutils.core import setup
else:
    d['install_requires'] = ['Twisted']

setup(**d)
