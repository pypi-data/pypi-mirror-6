# Copyright 2013 Christoph Reiter
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

_BACKENDS = []
_ACTIVE_BACKENDS = []


def init_backends():
    """Loads all backends"""

    global _BACKENDS, _ACTIVE_BACKENDS

    try:
        from .cffi_backend import CFFIBackend
    except ImportError:
        pass
    else:
        _BACKENDS.append(CFFIBackend)

    from .ctypes_backend import CTypesBackend

    _BACKENDS.append(CTypesBackend)
    _ACTIVE_BACKENDS = _BACKENDS[:]


def list_backends():
    """Returns a list of backends ordered by priority"""

    return _ACTIVE_BACKENDS


def get_backend(name):
    """Returns the backend by name or raises KeyError"""

    for backend in _ACTIVE_BACKENDS:
        if backend.NAME == name:
            return backend
    raise KeyError("Backend %r not available" % name)


def set_backend(name=None):
    """Set a prefered ffi backend (cffi, ctypes).

    set_backend() -- default
    set_backend("cffi") -- cffi first, others as fallback
    set_backend("ctypes") -- ctypes first, others as fallback
    """

    possible = list(_BACKENDS)
    if name is None:
        names = []
    else:
        names = name.split(",")

    # if explicitly asked, enable the null backend
    if "null" in names:
        from .null_backend import NullBackend
        possible.append(NullBackend)

    for name in reversed(names):
        for backend in list(possible):
            if backend.NAME == name:
                possible.remove(backend)
                possible.insert(0, backend)
                break
        else:
            raise LookupError("Unkown backend: %r" % name)

    _ACTIVE_BACKENDS[:] = possible


def VariableFactory():
    """Returns a callable the produces unique variable names"""

    def var_factory():
        var_factory.c += 1
        return "t%d" % var_factory.c
    var_factory.c = 0

    return var_factory


class Backend(object):
    """The backend interface."""

    def get_library(self, namespace):
        raise NotImplementedError

    def get_function(self, lib, symbol, args, ret,
                     method=False, self_name="", throws=False):
        raise NotImplementedError

    def get_constructor(self, gtype, args):
        raise NotImplementedError

    def get_callback(self, func, args, ret):
        raise NotImplementedError

    def get_type(self, type_, may_be_null=False):
        raise NotImplementedError
