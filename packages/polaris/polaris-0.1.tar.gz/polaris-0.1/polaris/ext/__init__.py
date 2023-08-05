"""
    polaris.ext
    ~~~~~~~~~~~

    :copyright: (c) 2013 Eleme, http://polaris.eleme.io
    :license: MIT
"""


def ext_cache(fn):
    """Cache for extension get
    """
    def wrapper(self, *args, **kwargs):
        if hasattr(self, "cache") and self.cache:
            @self.cache.cache_on_arguments()
            def cached_fn(*args, **kwargs):
                return fn(self, *args, **kwargs)
            return cached_fn(*args, **kwargs)
        else:
            return fn(self, *args, **kwargs)
    return wrapper


class PolarisExtension(object):
    """Base polaris extension class template.
    """

    def __init__(self, cache=None):
        self.cache = cache

    @ext_cache
    def get(self):
        raise NotImplementedError
