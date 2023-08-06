from __future__ import division

from functools import wraps
from inspect import ismethod
from datetime import timedelta
import copy

from django.core.cache import cache


def make_hash(obj):
    """Make a hash from an arbitrary nested dictionary, list, tuple or
    set.
    
    """
    if isinstance(obj, set) or isinstance(obj, tuple) or isinstance(obj, list):
        return hash(tuple([make_hash(e) for e in obj]))

    elif not isinstance(obj, dict):
        return hash(obj)

    new_obj = copy.deepcopy(obj)
    for k, v in new_obj.items():
        new_obj[k] = make_hash(v)

    return hash(tuple(frozenset(new_obj.items())))


def total_seconds(td):
    """Given a timedelta object, return the total number of seconds it
    represents.

    We avoid using .total_seconds(), since that requires Python 2.7.

    """
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6


def cached(function, **kwargs):
    """Return a version of this function that caches its results for
    the time specified.

    >>> def foo(x): print "called"; return 1
    >>> cached(foo)('whatever')
    called
    1
    >>> cached(foo)('whatever')
    1

    """
    cache_time = total_seconds(timedelta(**kwargs))
    if cache_time == 0:
        cache_time = None
    
    @wraps(function)
    def get_cache_or_call(*args, **kwargs):
        module_name = function.__module__

        if ismethod(function):
            class_name = function.im_class.__name__
        else:
            class_name = ""

        function_name = function.__name__

        cache_key = make_hash(
            (module_name, class_name, function_name, args, kwargs))

        cached_result = cache.get(cache_key)
        if cached_result is None:
            result = function(*args, **kwargs)

            # memcache returns None if the result isn't in the cache,
            # so we always store tuples
            result_to_cache = (result, None)
            cache.set(cache_key, result_to_cache, cache_time)

            return result
        else:
            result, dont_care = cached_result
            return result

    return get_cache_or_call
