# !/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.blueprints.static_react_task.static_react_task_builder import (
    StaticReactTaskBuilder,
)


class RemoteProcedureTaskBuilder(StaticReactTaskBuilder):
    """
    Builder for a "static task" that has access to remote queries.
    At the moment, simply a StaticReactTaskBuilder, as we will be using static react tasks
    in the same way.
    """

    pass
