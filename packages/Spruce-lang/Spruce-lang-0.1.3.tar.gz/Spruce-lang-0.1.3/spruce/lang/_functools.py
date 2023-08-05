"""Higher-order functions."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

from collections import namedtuple as _namedtuple
from functools import update_wrapper as _update_wrapper
from threading import Lock as _Lock


def lru_cache(maxsize=100, typed=False):

    """Memoize the wrapped function's most recent results.

    This caches the most recent *maxsize* results of the wrapped function.
    This can save time when an expensive or I/O bound function is
    periodically called with the same arguments.

    The arguments passed to the cached function must be hashable.

    If *maxsize* is null, then the LRU feature is disabled and the cache can
    grow without bound.  The LRU feature performs best when *maxsize* is a
    power of two.

    If *typed* is true, function arguments of different types will be cached
    separately.  For example, :code:`f(3)` and :code:`f(3.0)` will be
    treated as distinct calls with distinct results.

    To help measure the effectiveness of the cache and tune *maxsize*, the
    cached function is instrumented with a :meth:`!cache_info` method that
    returns a :func:`namedtuple <collections.namedtuple>` indicating
    :attr:`!hits`, :attr:`!misses`, :attr:`!maxsize`, and :attr:`!currsize`.
    In a multi-threaded environment, the :attr:`!hits` and :attr:`!misses`
    are approximate.

    The cached function also provides a :meth:`!cache_clear` method for
    clearing or invalidating the cache.

    The wrapped function is accessible through the cached function's
    :attr:`!__wrapped__` attribute.  This is useful for introspection, for
    bypassing the cache, or for rewrapping the function with a different
    cache.

    An `LRU (least recently used) cache`_ works best when the most recent
    calls are the best predictors of upcoming calls (for example, the most
    popular articles on a news server tend to change each day).  The cache's
    size limit assures that the cache does not grow without bound on
    long-running processes such as web servers.

    .. _LRU (least recently used) cache:
        http://en.wikipedia.org/wiki/Cache_algorithms#Least_Recently_Used

    .. note:: Source:
        :t:`Py2.6+ and Py3.0+ backport of Python 3.3's LRU Cache (Python
        recipe)`
        [`link
        <https://code.activestate.com/recipes/578078-py26-and-py30-backport-of-python-33s-lru-cache/>`_]

    """

    # Users should only access the lru_cache through its public API:
    #       cache_info, cache_clear, and f.__wrapped__
    # The internals of the lru_cache are encapsulated for thread safety and
    # to allow the implementation to change (including a possible C version).

    def decorating_function(user_function):

        cache = dict()
        # make statistics updateable non-locally
        stats = [0, 0]
        # names for the stats fields
        HITS, MISSES = 0, 1
        # separate positional and keyword args
        kwd_mark = (object(),)
        # bound method to lookup key or return None
        cache_get = cache.get
        # localize the global len() function
        _len = len
        # because linkedlist updates aren't threadsafe
        lock = _Lock()
        # root of the circular doubly linked list
        root = []
        # make updateable non-locally
        nonlocal_root = [root]
        # initialize by pointing to self
        root[:] = [root, root, None, None]
        # names for the link fields
        PREV, NEXT, KEY, RESULT = 0, 1, 2, 3

        def make_key(args, kwds, typed, tuple=tuple, sorted=sorted, type=type):
            # helper function to build a cache key from positional and keyword
            # args
            key = args
            if kwds:
                sorted_items = tuple(sorted(kwds.items()))
                key += kwd_mark + sorted_items
            if typed:
                key += tuple(type(v) for v in args)
                if kwds:
                    key += tuple(type(v) for k, v in sorted_items)
            return key

        if maxsize == 0:

            def wrapper(*args, **kwds):
                # no caching, just do a statistics update after a successful
                # call
                result = user_function(*args, **kwds)
                stats[MISSES] += 1
                return result

        elif maxsize is None:

            def wrapper(*args, **kwds):
                # simple caching without ordering or size limit
                key = make_key(args, kwds, typed) if kwds or typed else args
                # root used here as a unique not-found sentinel
                result = cache_get(key, root)
                if result is not root:
                    stats[HITS] += 1
                    return result
                result = user_function(*args, **kwds)
                cache[key] = result
                stats[MISSES] += 1
                return result

        else:

            def wrapper(*args, **kwds):
                # size limited caching that tracks accesses by recency
                key = make_key(args, kwds, typed) if kwds or typed else args
                with lock:
                    link = cache_get(key)
                    if link is not None:
                        # record recent use of the key by moving it to the
                        # front of the list
                        root, = nonlocal_root
                        link_prev, link_next, key, result = link
                        link_prev[NEXT] = link_next
                        link_next[PREV] = link_prev
                        last = root[PREV]
                        last[NEXT] = root[PREV] = link
                        link[PREV] = last
                        link[NEXT] = root
                        stats[HITS] += 1
                        return result
                result = user_function(*args, **kwds)
                with lock:
                    root = nonlocal_root[0]
                    if _len(cache) < maxsize:
                        # put result in a new link at the front of the list
                        last = root[PREV]
                        link = [last, root, key, result]
                        cache[key] = last[NEXT] = root[PREV] = link
                    else:
                        # use root to store the new key and result
                        root[KEY] = key
                        root[RESULT] = result
                        cache[key] = root
                        # empty the oldest link and make it the new root
                        root = nonlocal_root[0] = root[NEXT]
                        del cache[root[KEY]]
                        root[KEY] = None
                        root[RESULT] = None
                    stats[MISSES] += 1
                return result

        def cache_info():
            """Report cache statistics"""
            with lock:
                return _LruCacheInfo(stats[HITS], stats[MISSES], maxsize,
                                     len(cache))

        def cache_clear():
            """Clear the cache and cache statistics"""
            with lock:
                cache.clear()
                root = nonlocal_root[0]
                root[:] = [root, root, None, None]
                stats[:] = [0, 0]

        wrapper.__wrapped__ = user_function
        wrapper.cache_info = cache_info
        wrapper.cache_clear = cache_clear
        return _update_wrapper(wrapper, user_function)

    return decorating_function


_LruCacheInfo = \
    _namedtuple('CacheInfo', ['hits', 'misses', 'maxsize', 'currsize'])
