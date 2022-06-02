""" from mephisto.data_model._db_backed_meta import (
    MephistoDBBackedMeta,
    MephistoDataModelComponentMixin,
)
from mephisto.abstractions.database import MephistoDB
from typing import List, Optional, Mapping, TYPE_CHECKING, Any


class Tip(MephistoDataModelComponentMixin, metaclass=MephistoDBBackedMeta):
    def __init__(
        self, db: "MephistoDB", db_id: str, task_name: str, row: Optional[Mapping[str, Any]] = None
    ):

        self.db: "MephistoDB" = db
        if row is None:
          row = db.get_tip_by_task_name(task_name=task_name)
        assert row is not None, f"Given db_id {db_id} did not exist in given db"
        self.db_id: str =  """