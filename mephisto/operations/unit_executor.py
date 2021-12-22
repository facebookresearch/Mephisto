#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


class UnitExecutor:
    """
    This class is responsible for executing assignments and units, as well
    as managing setup and cleanup for each, closely leveraging TaskRunners
    and the TaskLauncher for a job to manage successful execution.
    """
