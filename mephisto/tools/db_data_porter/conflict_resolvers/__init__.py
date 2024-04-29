#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from importlib import import_module
from inspect import isclass
from pkgutil import iter_modules

from .base_merge_conflict_resolver import BaseMergeConflictResolver

# Import all conflict resolver classes except the base class.
# This is needed in case if user decides to write a custom class and
# this way its name will be available as a parameter for import command
current_dir = os.path.dirname(os.path.abspath(__file__))
for (_, module_name, _) in iter_modules([current_dir]):
    module = import_module(f"{__name__}.{module_name}")
    for attribute_name in dir(module):
        attribute = getattr(module, attribute_name)

        if (
            isclass(attribute)
            and issubclass(attribute, BaseMergeConflictResolver)
            and attribute is not BaseMergeConflictResolver
        ):
            globals().update({attribute.__name__: attribute})
