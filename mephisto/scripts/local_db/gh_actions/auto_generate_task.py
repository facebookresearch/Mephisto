# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from typing import Optional

from mdutils.mdutils import MdUtils

from mephisto.client.cli_commands import get_wut_arguments
from mephisto.scripts.local_db.gh_actions.auto_generate_blueprint import (
    add_object_args_table_info,
)


def main(root_path: Optional[str] = None):
    root_path = root_path or "../../../../"
    tasks_file = MdUtils(file_name=os.path.join(root_path, "docs/web/docs/reference/tasks.md"))

    tasks_file.new_header(level=1, title="Tasks")
    tasks_file.new_paragraph(
        "The tasks contain all of the related code required to set up a task run."
    )
    tasks_file.new_line()

    # Task args
    args = get_wut_arguments(["task"])
    arg_dict = args[0]
    add_object_args_table_info(tasks_file, arg_dict)

    tasks_file.create_md_file()


if __name__ == "__main__":
    main()
