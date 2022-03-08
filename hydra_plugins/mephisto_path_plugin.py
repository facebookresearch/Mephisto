#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from hydra.core.config_search_path import ConfigSearchPath
from hydra.plugins.search_path_plugin import SearchPathPlugin

from mephisto.utils.dirs import get_root_dir
from mephisto.operations.config_handler import DEFAULT_CONFIG_FOLDER
import os


class MephistoSearchPathPlugin(SearchPathPlugin):
    def manipulate_search_path(self, search_path: ConfigSearchPath) -> None:
        # Appends the search path for this plugin to the end of the search path
        profile_path = os.path.join(get_root_dir(), "hydra_configs")
        profile_path_user = os.path.join(DEFAULT_CONFIG_FOLDER, "hydra_configs")

        search_path.append(provider="mephisto-profiles", path=f"file://{profile_path}")
        search_path.append(
            provider="mephisto-profiles-user", path=f"file://{profile_path_user}"
        )
