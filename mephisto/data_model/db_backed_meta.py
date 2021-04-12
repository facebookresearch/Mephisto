#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List, Optional, Tuple, Mapping, Dict, Any, TYPE_CHECKING

from abc import ABCMeta

if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB


def base_db_backed_call(my_super, cls, a, kw):
    """
    Metaclass __call__ method, pulled out so we can have separate
    versions with and without ABCMeta.

    Checks the database first for an optimized load, then loads
    normally, then caches the result if desired
    """
    db = a[0]
    db_id = a[1]
    row = kw.get("row")
    loaded_val = db.optimized_load(cls, db_id, row)
    if loaded_val is None:
        loaded_val = my_super.__call__(*a, **kw)
        db.cache_result(cls, loaded_val)
    return loaded_val


class MephistoDBBackedABCMeta(ABCMeta):
    """
    Metaclass that overrides `call` to allow the current `MephistoDB` an
    opportunity to do an optimized load if desired. Provides more control
    over the creation of objects than normal.

    Extends ABCMeta, so that we can use this for the abstract classes
    """

    def __call__(cls, *a, **kw):
        return base_db_backed_call(super(), cls, a, kw)


class MephistoDBBackedMeta(type):
    """
    Metaclass that overrides `call` to allow the current `MephistoDB` an
    opportunity to do an optimized load if desired. Provides more control
    over the creation of objects than normal.
    """

    def __call__(cls, *a, **kw):
        return base_db_backed_call(super(), cls, a, kw)
