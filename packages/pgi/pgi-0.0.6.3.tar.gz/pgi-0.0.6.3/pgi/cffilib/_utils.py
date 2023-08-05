# Copyright 2013 Christoph Reiter
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.


import re


def _unpack_zeroterm_char_array(ffi, ptr):
    assert ptr

    index = 0
    current = ptr[index]
    array = []
    while current:
        array.append(ffi.string(current))
        index += 1
        current = ptr[index]
    return array


def _create_enum_class(ffi, type_name, prefix):
    """Returns a new shiny class for the given enum type"""

    class _template(int):
        _map = {}

        def __repr__(self):
            return "%s.%s" % (type(self).__name__,
                              self._map.get(self, "__UNKNOWN__"))

    cls = type(type_name, _template.__bases__, dict(_template.__dict__))
    prefix_len = len(prefix)
    for value, name in ffi.typeof(type_name).elements.items():
        assert name[:prefix_len] == prefix
        name = name[prefix_len:]
        setattr(cls, name, cls(value))
        cls._map[value] = name

    return cls


def _fixup_cdef_enums(string, reg=re.compile(r"=\s*(\d+)\s*<<\s*(\d+)")):
    """Converts some common enum expressions to constants"""

    def repl_shift(match):
        return "= %s" % str(int(match.group(1)) << int(match.group(2)))
    return reg.sub(repl_shift, string)
