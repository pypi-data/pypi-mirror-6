"""
    polaris.utils
    ~~~~~~~~~~~~~

    :copyright: (c) 2013 Eleme, http://polaris.eleme.io
    :license: MIT
"""

import hashlib


def import_string(import_name):
    """Imports an object based on a string. This is useful if you want to
    use import paths as endpoints or something similar.

    :param import_name: the dotted name for the object to import.
    :return: imported object
    """
    # force the import name to automatically convert to strings
    import_name = str(import_name)
    if ':' in import_name:
        module, obj = import_name.split(':', 1)
        return getattr(__import__(module, None, None, [obj]), obj)
    elif '.' in import_name:
        module, obj = import_name.rsplit('.', 1)
        return getattr(__import__(module, None, None, [obj]), obj)
    else:
        return __import__(import_name)


def kw_generator(namespace, fn, **kw):
    fname = fn.__name__

    def generate_key(*arg, **kw):
        args_str = ",".join([str(s) for s in arg] +
                            ["{}={}".format(k, kw[k]) for k in sorted(kw)])
        hashed_str = hashlib.md5(args_str.encode("utf-8")).hexdigest()
        return "{}_{}|{}".format(namespace, fname, hashed_str)
    return generate_key
