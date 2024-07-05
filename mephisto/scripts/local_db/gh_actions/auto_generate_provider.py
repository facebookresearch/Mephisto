# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from typing import Optional

from mdutils.mdutils import MdUtils

from mephisto.client.cli_wut_commands import get_wut_arguments
from mephisto.operations.registry import (
    get_valid_provider_types,
)
from mephisto.scripts.local_db.gh_actions.auto_generate_blueprint import (
    add_object_args_table_info,
)


def main(root_path: Optional[str] = None):
    root_path = root_path or "../../../../"
    provider_file = MdUtils(
        file_name=os.path.join(root_path, "docs/web/docs/reference/providers.md")
    )
    provider_file.new_header(level=1, title="Providers")
    provider_file.new_paragraph(
        "Crowd providers standardize access to external crowd workers, "
        "by wrapping external API communication through a standardized interface."
    )
    provider_file.new_line()

    valid_provider_types = get_valid_provider_types()
    for provider_type in valid_provider_types:
        provider_file.new_line()
        provider_file.new_header(level=2, title=provider_type.replace("_", " "))
        args = get_wut_arguments(("provider={provider_name}".format(provider_name=provider_type),))
        arg_dict = args[0]
        add_object_args_table_info(provider_file, arg_dict)

    provider_file.create_md_file()


if __name__ == "__main__":
    main()
