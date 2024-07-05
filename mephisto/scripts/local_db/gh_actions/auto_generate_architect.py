# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from typing import Optional

from mdutils.mdutils import MdUtils

from mephisto.client.cli_wut_commands import get_wut_arguments
from mephisto.operations.registry import get_valid_architect_types
from mephisto.scripts.local_db.gh_actions.auto_generate_blueprint import (
    add_object_args_table_info,
)


def main(root_path: Optional[str] = None):
    root_path = root_path or "../../../../"
    architect_file = MdUtils(
        file_name=os.path.join(root_path, "docs/web/docs/reference/architects.md")
    )

    architect_file.new_header(level=1, title="Architects")
    architect_file.new_paragraph(
        "Architects contain the logic surrounding deploying a server "
        "that workers will be able to access."
    )
    architect_file.new_line()

    valid_architect_types = get_valid_architect_types()
    for architect_type in valid_architect_types:
        architect_file.new_line()
        architect_file.new_header(level=2, title=architect_type.replace("_", " "))
        args = get_wut_arguments(
            ("architect={architect_name}".format(architect_name=architect_type),)
        )
        arg_dict = args[0]
        add_object_args_table_info(architect_file, arg_dict)

    architect_file.create_md_file()


if __name__ == "__main__":
    main()
