=====================
Redis Tools (retools)
=====================

``retools`` is a package of Redis tools. It's aim is to provide a variety of
Redis backed Python tools that are always 100% unit tested, fast, efficient,
and utilize the capabilities of Redis.

Current tools in ``retools``:

* Caching
* Global Lock

On the horizon for future implementation:

* A worker/job processing system similar to Celery but based on how Ruby's
  Resque system works.

.. image:: https://secure.travis-ci.org/bbangert/retools.png?branch=master
   :alt: Build Status
   :target: https://secure.travis-ci.org/bbangert/retools


Caching
=======

A high performance caching system that can act as a drop-in replacement for
Beaker's caching. Unlike Beaker's caching, this utilizes Redis for distributed
write-locking dogpile prevention. It also collects hit/miss cache statistics
along with recording what regions are used by which functions and arguments.

Example::

    from retools.cache import CacheRegion, cache_region, invalidate_function

    CacheRegion.add_region('short_term', expires=3600)

    @cache_region('short_term')
    def slow_function(*search_terms):
        # Do a bunch of work
        return results

    my_results = slow_function('bunny')

    # Invalidate the cache for 'bunny'
    invalidate_function(slow_function, [], 'bunny')


Differences from Beaker
-----------------------

Unlike Beaker's caching system, this is built strictly for Redis. As such, it
adds several features that Beaker doesn't possess:

* A distributed write-lock so that only one writer updates the cache at a time
  across a cluster.
* Hit/Miss cache statistics to give you insight into what caches are less
  effectively utilized (and may need either higher expiration times, or just
  not very worthwhile to cache).
* Very small, compact code-base with 100% unit test coverage.


Locking
=======

A Redis based lock implemented as a Python context manager, based on `Chris
Lamb's example
<http://chris-lamb.co.uk/2010/06/07/distributing-locking-python-and-redis/>`_.

Example::

    from retools.lock import Lock

    with Lock('a_key', expires=60, timeout=10):
        # do something that should only be done one at a time


License
=======

``retools`` is offered under the MIT license.


Authors
=======

``retools`` is made available by `Ben Bangert`.


=========
Changelog
=========

0.4 (01/27/2014)
================

Features
--------

- Added limiter functionality. Pull request #22, by Bernardo Heynemann.

0.3 (08/13/2012)
================

Bug Fixes
---------

- Call redis.expire with proper expires value for RedisLock. Patch by
  Mike McCabe.
- Use functools.wraps to preserve doc strings for cache_region. Patch by
  Daniel Holth.

API Changes
-----------

- Added get_job/get_jobs methods to QueueManager class to get information
  on a job or get a list of jobs for a queue.

0.2 (02/01/2012)
================

Bug Fixes
---------

- Critical fix for caching that prevents old values from being displayed
  forever. Thanks to Daniel Holth for tracking down the problem-aware.
- Actually sets the Redis expiration for a value when setting the cached
  value in Redis. This defaults to 1 week.

Features
--------

- Statistics for the cache is now optional and can be disabled to slightly
  reduce the Redis queries used to store/retrieve cache data.
- Added first revision of worker/job Queue system, with event support.

Internals
---------

- Heavily refactored ``Connection`` to not be a class singleton, instead
  a global_connection instance is created and used by default.
- Increased conditional coverage to 100% (via instrumental_).

Backwards Incompatibilities
---------------------------

- Changing the default global Redis connection has changed semantics, instead
  of using ``Connection.set_default``, you should set the global_connection's
  redis property directly::

      import redis
      from retools import global_connection

      global_connection.redis = redis.Redis(host='myhost')


Incompatibilities
-----------------

- Removed clear argument from invalidate_region, as removing keys from the
  set but not removing the hit statistics can lead to data accumulating in
  Redis that has no easy removal other than .keys() which should not be run
  in production environments.

- Removed deco_args from invalidate_callable (invalidate_function) as its
  not actually needed since the namespace is already on the callable to
  invalidate.


0.1 (07/08/2011)
================

Features
--------

- Caching in a similar style to Beaker, with hit/miss statistics, backed by
  a Redis global write-lock with old values served to prevent the dogpile
  effect
- Redis global lock

.. _instrumental: http://pypi.python.org/pypi/instrumental


