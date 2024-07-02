# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import re
from copy import deepcopy
from typing import Optional

from mdutils.mdutils import MdUtils

from mephisto.client.cli_commands import get_wut_arguments
from mephisto.operations.registry import get_valid_blueprint_types


def _remove_multiple_spaces(string: str) -> str:
    string = re.compile(r"\s+").sub(" ", string).strip()
    return string


def add_object_args_table_info(file, arg_dict):
    provider_desc = _remove_multiple_spaces(arg_dict["desc"])
    if provider_desc:
        file.new_line(provider_desc, align="left")
        file.new_line()

    arg_keys = list(arg_dict["args"].keys())
    first_arg = list(arg_dict["args"].keys())[0]
    first_arg_keys = list(arg_dict["args"][first_arg].keys())

    list_of_strings = deepcopy(first_arg_keys)

    for cur_key in arg_keys:
        extension_list = []
        for first_arg_key in first_arg_keys:
            item_content = arg_dict["args"][cur_key][first_arg_key]
            item_to_append = (
                "".join(item_content.splitlines())
                if isinstance(item_content, str)
                else item_content
            )
            if isinstance(item_to_append, str):
                item_to_append = _remove_multiple_spaces(item_to_append)
                if item_to_append.rfind("mephisto/") != -1:
                    item_to_append = item_to_append[
                        item_to_append.rfind("mephisto/") : len(item_to_append)
                    ]

            extension_list.append(item_to_append)

        list_of_strings.extend(extension_list)

    # Add 1 to rows to account for header row
    file.new_table(
        rows=len(arg_keys) + 1,
        columns=len(first_arg_keys),
        text=list_of_strings,
        text_align="left",
    )


def main(root_path: Optional[str] = None):
    root_path = root_path or "../../../../"
    blueprint_file = MdUtils(
        file_name=os.path.join(root_path, "docs/web/docs/reference/blueprints.md")
    )
    blueprint_file.new_header(level=1, title="Blueprints")
    blueprint_file.new_paragraph(
        "The blueprints contain all of the related code required to set up a task run."
    )
    blueprint_file.new_line()

    valid_blueprint_types = get_valid_blueprint_types()
    for blueprint_type in valid_blueprint_types:
        blueprint_file.new_line()
        blueprint_file.new_header(level=2, title=blueprint_type.replace("_", " "))
        args = get_wut_arguments(
            ("blueprint={blueprint_name}".format(blueprint_name=blueprint_type),)
        )
        arg_dict = args[0]
        add_object_args_table_info(blueprint_file, arg_dict)

    blueprint_file.create_md_file()


if __name__ == "__main__":
    main()
