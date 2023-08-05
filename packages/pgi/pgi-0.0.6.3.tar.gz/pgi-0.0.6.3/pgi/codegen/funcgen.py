# Copyright 2012,2013 Christoph Reiter
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

import traceback

from .backend import list_backends
from .utils import CodeBlock
from pgi.util import escape_name, escape_builtin
from .arguments import get_argument_class, ErrorArgument
from .returnvalues import get_return_class


def get_type_name(type_):
    """Gives a name for a type that is suitable for a docstring.

    int -> "int"
    Gtk.Window -> "Gtk.Window"
    [int] -> "[int]"
    {int: Gtk.Button} -> "{int: Gtk.Button}"
    """

    if isinstance(type_, basestring):
        return type_
    elif isinstance(type_, list):
        assert len(type_) == 1
        return "[%s]" % get_type_name(type_[0])
    elif isinstance(type_, dict):
        assert len(type_) == 1
        key, value = type_.popitem()
        return "{%s: %s}" % (get_type_name(key), get_type_name(value))
    elif type_.__module__ in "__builtin__":
        return type_.__name__
    else:
        return "%s.%s" % (type_.__module__, type_.__name__)


def build_docstring(func_name, args, ret, throws):
    """Create a docstring in the form:
        name(in_name: type) -> (ret_type, out_name: type)
    """

    out_args = []
    if ret:
        if ret.py_type is None:
            out_args.append("unknown")
        else:
            tname = get_type_name(ret.py_type)
            if ret.may_return_null:
                tname += " or None"
            out_args.append(tname)

    in_args = []
    for arg in args:
        if arg.is_aux:
            continue

        if arg.in_var:
            if arg.py_type is None:
                in_args.append(arg.in_var)
            else:
                tname = get_type_name(arg.py_type)
                if arg.may_be_null:
                    tname += " or None"
                in_args.append("%s: %s" % (arg.in_var, tname))

        if arg.out_var:
            if arg.py_type is None:
                out_args.append(arg.name)
            else:
                tname = get_type_name(arg.py_type)
                # When can we assume that out args return None?
                out_args.append("%s: %s" % (arg.name, tname))

    in_def = ", ".join(in_args)

    if not out_args:
        out_def = "None"
    elif len(out_args) == 1:
        out_def = out_args[0]
    else:
        out_def = "(%s)" % ", ".join(out_args)

    error = ""
    if throws:
        error = "raises "

    return "%s(%s) %s-> %s" % (func_name, in_def, error, out_def)


def _generate_function(backend, info, arg_infos, arg_types,
                       return_type, method, throws):

    args = []
    for arg_info, arg_type in zip(arg_infos, arg_types):
        cls = get_argument_class(arg_type)
        name = escape_name(escape_builtin(arg_info.name))
        args.append(cls(name, args, backend, arg_info, arg_type))

    cls = get_return_class(return_type)
    return_value = cls(info, return_type, args, backend)

    if throws:
        args.append(ErrorArgument(args, backend))

    # setup
    for arg in args:
        arg.setup()

    return_value.setup()

    body = CodeBlock()

    # pre call
    for arg in args:
        if arg.is_aux or arg.ignore:
            continue
        block = arg.pre_call()
        if block:
            block.write_into(body)

    block = return_value.pre_call()
    if block:
        block.write_into(body)

    # generate call
    lib = backend.get_library(info.namespace)
    symbol = info.symbol
    block, svar, func = backend.get_function(lib, symbol, args,
                                             return_value, method,
                                             "self", throws)
    if block:
        block.write_into(body)

    # do the call
    call_vars = [a.call_var for a in args if a.call_var]
    if method:
        call_vars.insert(0, svar)
    call_block, var = backend.parse("$ret = $func($args)",
                                    func=func, args=", ".join(call_vars))
    call_block.write_into(body)
    ret = var["ret"]

    out = []

    # handle errors first
    if throws:
        error_arg = args.pop()
        block = error_arg.post_call()
        if block:
            block.write_into(body)

    # process return value
    block, return_var = return_value.post_call(ret)
    if block:
        block.write_into(body)
    if return_var:
        out.append(return_var)

    # process out args
    for arg in args:
        if arg.is_aux or arg.ignore:
            continue
        block = arg.post_call()
        if block:
            block.write_into(body)
        if arg.out_var:
            out.append(arg.out_var)

    if len(out) == 1:
        body.write_line("return %s" % out[0])
    elif len(out) > 1:
        body.write_line("return (%s)" % ", ".join(out))

    # build final function block

    func_name = escape_name(info.name)
    # handle empty string function names
    if func_name == "":
        func_name = "_"

    docstring = build_docstring(func_name, args,
                                return_var and return_value, throws)

    names = [a.in_var for a in args if not a.is_aux and a.in_var]
    if method:
        names.insert(0, "self")
    names = ", ".join(names)

    main, var = backend.parse("""
# backend: $backend_name
def $func_name($func_args):
    '''$docstring'''

    $func_body
""", backend_name=backend.NAME, func_args=names, docstring=docstring,
     func_body=body, func_name=func_name)

    func = main.compile()[func_name]
    func._code = main
    func.__doc__ = docstring

    return func


def generate_function(info, method=False, throws=False):
    arg_infos = info.get_args()
    arg_types = [a.get_type() for a in arg_infos]
    return_type = info.get_return_type()

    func = None
    messages = []
    for backend in list_backends():
        instance = backend()
        try:
            func = _generate_function(instance, info, arg_infos, arg_types,
                                      return_type, method, throws)
        except NotImplementedError:
            messages.append("%s: %s" % (backend.NAME, traceback.format_exc()))
        else:
            break

    if func:
        return func

    raise NotImplementedError("\n".join(messages))
