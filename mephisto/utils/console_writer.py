#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import traceback
from types import FunctionType
from typing import Any
from typing import Optional

from rich import print as rich_print


class ConsoleWriter:
    """
    This class allows to consistently write logs to the console, and apply colored highlights.
    To make it easily interchangeable with standard Python logger, it uses same method names.

    Usage:
        logger = ConsoleWriter()
        logger.info("Some message")

        # to interchange with Python logger, just change one line in the module
        logger = get_logger(name=__name__)
    """

    _writer = None

    def __init__(self, printer: Optional[FunctionType] = None):
        self._writer = printer or rich_print  # by default, we use `rich.print`

    def info(self, value: Any):
        self._writer(str(value))

    def debug(self, value: Any):
        self._writer(str(value))

    def warning(self, value: Any):
        self._writer(str(value))

    def error(self, value: Any):
        self._writer(str(value))

    def exception(self, value: Any):
        self.error(value)
        rich_print(traceback.format_exc())
