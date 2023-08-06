# -*- coding: utf-8 -*-
__version__ = '1.0.0'
__versionfull__ = __version__

import base64
import uuid
import hashlib
import inspect
import functools
import warnings
import logging

from django.conf import settings
from django.core.cache import cache as default_cache

logger = logging.getLogger(__name__)


def function_namespace(f, args=None):
    """
    Attempts to returns unique namespace for function
    """
    m_args = inspect.getargspec(f)[0]

    if len(m_args) and args:
        if m_args[0] == 'self':
            return '%s.%s.%s' % (f.__module__, args[0].__class__.__name__, f.__name__)
        elif m_args[0] == 'cls':
            return '%s.%s.%s' % (f.__module__, args[0].__name__, f.__name__)

    if hasattr(f, '__func__'):
        return '%s.%s.%s' % (f.__module__, f.__self__.__class__.__name__, f.__name__)
    elif hasattr(f, '__class__'):
        return '%s.%s.%s' % (f.__module__, f.__class__.__name__, f.__name__)
    else:
        return '%s.%s' % (f.__module__, f.__name__)


class Memoizer(object):
    """
    This class is used to control the memoizer objects.
    """

    def __init__(self):
        self.cache = default_cache
        self.cache_prefix = 'memoize'

    def get(self, *args, **kwargs):
        "Proxy function for internal cache object."
        return self.cache.get(*args, **kwargs)

    def set(self, *args, **kwargs):
        "Proxy function for internal cache object."
        self.cache.set(*args, **kwargs)

    def add(self, *args, **kwargs):
        "Proxy function for internal cache object."
        self.cache.add(*args, **kwargs)

    def delete(self, *args, **kwargs):
        "Proxy function for internal cache object."
        self.cache.delete(*args, **kwargs)

    def delete_many(self, *args, **kwargs):
        "Proxy function for internal cache object."
        self.cache.delete_many(*args, **kwargs)

    def clear(self):
        "Proxy function for internal cache object."
        self.cache.clear()

    def get_many(self, *args, **kwargs):
        "Proxy function for internal cache object."
        return self.cache.get_many(*args, **kwargs)

    def set_many(self, *args, **kwargs):
        "Proxy function for internal cache object."
        self.cache.set_many(*args, **kwargs)

    def _memvname(self, funcname):
        return funcname + '_memver'

    def memoize_make_version_hash(self):
        return base64.b64encode(uuid.uuid4().bytes)[:6].decode('utf-8')

    def memoize_make_cache_key(self, make_name=None):
        """
        Function used to create the cache_key for memoized functions.
        """
        def make_cache_key(f, *args, **kwargs):
            fname = function_namespace(f, args)

            version_key = self._memvname(fname)
            version_data = self.cache.get(version_key)

            if version_data is None:
                version_data = self.memoize_make_version_hash()
                self.cache.set(version_key, version_data)

            cache_key = hashlib.md5()

            #: this should have to be after version_data, so that it
            #: does not break the delete_memoized functionality.
            if callable(make_name):
                altfname = make_name(fname)
            else:
                altfname = fname

            if callable(f):
                keyargs, keykwargs = self.memoize_kwargs_to_args(f,
                                                                 *args,
                                                                 **kwargs)
            else:
                keyargs, keykwargs = args, kwargs

            try:
                updated = "{0}{1}{2}".format(altfname, keyargs, keykwargs)
            except AttributeError:
                updated = "%s%s%s" % (altfname, keyargs, keykwargs)

            cache_key.update(updated.encode('utf-8'))
            cache_key = base64.b64encode(cache_key.digest())[:16]
            cache_key = cache_key.decode('utf-8')
            cache_key += version_data

            if self.cache_prefix:
                cache_key = '%s:%s' % (self.cache_prefix, cache_key)

            return cache_key
        return make_cache_key

    def memoize_kwargs_to_args(self, f, *args, **kwargs):
        #: Inspect the arguments to the function
        #: This allows the memoization to be the same
        #: whether the function was called with
        #: 1, b=2 is equivilant to a=1, b=2, etc.
        new_args = []
        arg_num = 0
        argspec = inspect.getargspec(f)

        args_len = len(argspec.args)
        for i in range(args_len):
            if i == 0 and argspec.args[i] in ('self', 'cls'):
                #: use the repr of the class instance
                #: this supports instance methods for
                #: the memoized functions, giving more
                #: flexibility to developers
                arg = repr(args[0])
                arg_num += 1
            elif argspec.args[i] in kwargs:
                arg = kwargs[argspec.args[i]]
            elif arg_num < len(args):
                arg = args[arg_num]
                arg_num += 1
            elif abs(i-args_len) <= len(argspec.defaults):
                arg = argspec.defaults[i-args_len]
                arg_num += 1
            else:
                arg = None
                arg_num += 1

            #: Attempt to convert all arguments to a
            #: hash/id or a representation?
            #: Not sure if this is necessary, since
            #: using objects as keys gets tricky quickly.
            # if hasattr(arg, '__class__'):
            #     try:
            #         arg = hash(arg)
            #     except:
            #         arg = repr(arg)

            #: Or what about a special __cacherepr__ function
            #: on an object, this allows objects to act normal
            #: upon inspection, yet they can define a representation
            #: that can be used to make the object unique in the
            #: cache key. Given that a case comes across that
            #: an object "must" be used as a cache key
            # if hasattr(arg, '__cacherepr__'):
            #     arg = arg.__cacherepr__

            new_args.append(arg)

        return tuple(new_args), {}

    def memoize(self, timeout=None, make_name=None, unless=None):
        """
        Use this to cache the result of a function, taking its arguments into
        account in the cache key.

        Information on
        `Memoization <http://en.wikipedia.org/wiki/Memoization>`_.

        Example::

            @memoize(timeout=50)
            def big_foo(a, b):
                return a + b + random.randrange(0, 1000)

        .. code-block:: pycon

            >>> big_foo(5, 2)
            753
            >>> big_foo(5, 3)
            234
            >>> big_foo(5, 2)
            753

        .. note::

            The returned decorated function now has three function attributes
            assigned to it.

                **uncached**
                    The original undecorated function. readable only

                **cache_timeout**
                    The cache timeout value for this function. For a custom value
                    to take affect, this must be set before the function is called.

                    readable and writable

                **make_cache_key**
                    A function used in generating the cache_key used.

                    readable and writable


        :param timeout: Default None. If set to an integer, will cache for that
                        amount of time. Unit of time is in seconds.
        :param make_name: Default None. If set this is a function that accepts
                          a single argument, the function name, and returns a
                          new string to be used as the function name. If not set
                          then the function name is used.
        :param unless: Default None. Cache will *always* execute the caching
                       facilities unelss this callable is true.
                       This will bypass the caching entirely.

        """

        def memoize(f):
            @functools.wraps(f)
            def decorated_function(*args, **kwargs):
                #: bypass cache
                if callable(unless) and unless() is True:
                    return f(*args, **kwargs)

                try:
                    cache_key = decorated_function.make_cache_key(f, *args, **kwargs)
                    rv = self.cache.get(cache_key)
                except Exception:
                    if settings.DEBUG:
                        raise
                    logger.exception("Exception possibly due to cache backend.")
                    return f(*args, **kwargs)

                if rv is None:
                    rv = f(*args, **kwargs)
                    try:
                        self.cache.set(cache_key, rv,
                                   timeout=decorated_function.cache_timeout)
                    except Exception:
                        if settings.DEBUG:
                            raise
                        logger.exception("Exception possibly due to cache backend.")
                        return f(*args, **kwargs)
                return rv

            decorated_function.uncached = f
            decorated_function.cache_timeout = timeout
            decorated_function.make_cache_key = self.memoize_make_cache_key(make_name)
            decorated_function.delete_memoized = lambda: self.delete_memoized(f)

            return decorated_function
        return memoize

    def delete_memoized(self, f, *args, **kwargs):
        """
        Deletes the specified functions caches, based by given parameters.
        If parameters are given, only the functions that were memoized with them
        will be erased. Otherwise all versions of the caches will be forgotten.

        Example::

            @memoize(timeout=50)
            def random_func():
                return random.randrange(1, 50)

            @memoize()
            def param_func(a, b):
                return a+b+random.randrange(1, 50)

        .. code-block:: pycon

            >>> random_func()
            43
            >>> random_func()
            43
            >>> delete_memoized('random_func')
            >>> random_func()
            16
            >>> param_func(1, 2)
            32
            >>> param_func(1, 2)
            32
            >>> param_func(2, 2)
            47
            >>> delete_memoized('param_func', 1, 2)
            >>> param_func(1, 2)
            13
            >>> param_func(2, 2)
            47


        :param fname: Name of the memoized function, or a reference to the function.
        :param \*args: A list of positional parameters used with memoized function.
        :param \**kwargs: A dict of named parameters used with memoized function.

        .. note::

            django-memoize uses inspect to order kwargs into positional args when
            the function is memoized. If you pass a function reference into ``fname``
            instead of the function name, django-memoize will be able to place
            the args/kwargs in the proper order, and delete the positional cache.

            However, if ``delete_memozied`` is just called with the name of the
            function, be sure to pass in potential arguments in the same order
            as defined in your function as args only, otherwise django-memoize
            will not be able to compute the same cache key.

        .. note::

            django-memoize maintains an internal random version hash for the function.
            Using delete_memoized will only swap out the version hash, causing
            the memoize function to recompute results and put them into another key.

            This leaves any computed caches for this memoized function within the
            caching backend.

            It is recommended to use a very high timeout with memoize if using
            this function, so that when the version has is swapped, the old cached
            results would eventually be reclaimed by the caching backend.
        """
        if not callable(f):
            raise DeprecationWarning("Deleting messages by relative name is no longer"
                          " reliable, please switch to a function reference")

        _fname = function_namespace(f, args)

        try:
            if not args and not kwargs:
                version_key = self._memvname(_fname)
                version_data = self.memoize_make_version_hash()
                self.cache.set(version_key, version_data)
            else:
                cache_key = f.make_cache_key(f.uncached, *args, **kwargs)
                self.cache.delete(cache_key)
        except Exception:
            if settings.DEBUG:
                raise
            logger.exception("Exception possibly due to cache backend.")

    def delete_memoized_verhash(self, f, *args):
        """
        Delete the version hash associated with the function.

        .. warning::

            Performing this operation could leave keys behind that have
            been created with this version hash. It is up to the application
            to make sure that all keys that may have been created with this
            version hash at least have timeouts so they will not sit orphaned
            in the cache backend.
        """
        if not callable(f):
            raise DeprecationWarning("Deleting messages by relative name is no longer"
                          " reliable, please use a function reference")

        _fname = function_namespace(f, args)

        try:
            version_key = self._memvname(_fname)
            self.cache.delete(version_key)
        except Exception:
            if settings.DEBUG:
                raise
            logger.exception("Exception possibly due to cache backend.")


# Memoizer instance
_memoizer = Memoizer()

memoize = _memoizer.memoize
delete_memoized = _memoizer.delete_memoized
delete_memoized_verhash = _memoizer.delete_memoized_verhash
