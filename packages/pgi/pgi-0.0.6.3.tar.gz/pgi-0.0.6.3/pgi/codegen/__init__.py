# Copyright 2012,2013 Christoph Reiter
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

from .backend import set_backend
from .funcgen import generate_function
from .construct import generate_constructor
from .siggen import generate_signal_callback, generate_callback
from .fieldgen import generate_field_getter, generate_field_setter


set_backend = set_backend
generate_function = generate_function
generate_constructor = generate_constructor
generate_signal_callback = generate_signal_callback
generate_callback = generate_callback


from .backend import init_backends
init_backends()
del init_backends
