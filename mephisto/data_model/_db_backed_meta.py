#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import asyncio
from functools import partial
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


class MephistoDataModelComponentMixin:
    """
    Mixin that provides the `get` method for classes in the Mephisto data model
    """

    @classmethod
    def get(
        cls,
        db: "MephistoDB",
        db_id: str,
        row: Optional[Mapping[str, Any]] = None,
        _used_new_call: bool = False,
    ):
        loaded_val = db.optimized_load(cls, db_id, row)
        if loaded_val is None:
            loaded_val = cls.__call__(db, db_id, row=row, _used_new_call=True)
            db.cache_result(cls, loaded_val)
        return loaded_val

    @classmethod
    async def async_get(
        cls,
        db: "MephistoDB",
        db_id: str,
        row: Optional[Mapping[str, Any]] = None,
    ):
        """
        Async wrapper for retrieving from the db. In the future, if a db implements
        a different get method, will call that instead.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            partial(
                cls.get,
                db,
                db_id,
                row=row,
            ),
        )
