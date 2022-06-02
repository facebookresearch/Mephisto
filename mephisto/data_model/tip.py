from mephisto.data_model._db_backed_meta import (
    MephistoDBBackedMeta,
    MephistoDataModelComponentMixin,
)
from mephisto.abstractions.database import MephistoDB
from typing import Optional, Mapping, Any


class Tip(MephistoDataModelComponentMixin, metaclass=MephistoDBBackedMeta):
    """
    This class contains all the required tidbits for the Tip datamodel.
    """

    def __init__(
        self,
        db: "MephistoDB",
        db_id: str,
        row: Optional[Mapping[str, Any]] = None,
    ):

        self.db: "MephistoDB" = db
        if row is None:
            row = db.get_tip(tip_id=db_id)
        assert row is not None, f"Given db_id {db_id} did not exist in given db"
        self.db_id: str = row["tip_id"]
        self.task_name: str = row["task_name"]
        self.tip_text: str = row["tip_text"]

    # TODO: Add possible helper methods here
    def test(self):
        print("helper method")
