# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os

from mephisto.scripts.local_db.gh_actions import auto_generate_architect
from mephisto.scripts.local_db.gh_actions import auto_generate_blueprint
from mephisto.scripts.local_db.gh_actions import auto_generate_provider
from mephisto.scripts.local_db.gh_actions import auto_generate_requester
from mephisto.scripts.local_db.gh_actions import auto_generate_task


def main():
    root_path = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )

    auto_generate_architect.main(root_path)
    auto_generate_blueprint.main(root_path)
    auto_generate_provider.main(root_path)
    auto_generate_requester.main(root_path)
    auto_generate_task.main(root_path)


if __name__ == "__main__":
    main()
