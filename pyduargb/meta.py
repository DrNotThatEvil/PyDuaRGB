from __future__ import print_function, absolute_import


class _Singleton(type):
    """ A Metaclass that creates a Singleton base class when created. """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(
                *args, **kwargs)
        return cls._instances[cls]


class Singleton(_Singleton('SingletonMeta', (object,), {})):
    @classmethod
    def destroy(cls):
        del cls._instances[cls]
