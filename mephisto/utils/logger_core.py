#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import logging
import os
from logging.config import dictConfig
from typing import Optional, Dict, Set
from werkzeug.utils import import_string

BOLD_RED = "\u001b[31;1m"
RESET = "\u001b[0m"
LOGGING_MODULE = os.environ.get("LOGGING_MODULE", "mephisto.configs.logging")

logging_module = import_string(LOGGING_MODULE)
loggers: Dict[str, logging.Logger] = {}
global_log_level = logging.INFO
_seen_logs: Set[str] = set()


def warn_once(msg: str) -> None:
    """
    Log a warning, but only once.

    :param str msg: Message to display
    """
    global _seen_logs
    if msg not in _seen_logs:
        _seen_logs.add(msg)
        logging.warning(msg)


def set_mephisto_log_level(verbose: Optional[bool] = None, level: Optional[str] = None):
    """
    Set the global level for Mephisto logging, from
    which all other classes will set their logging.

    Verbose sets an option between DEBUG and INFO, while level allows setting
    a specific level, and takes precedence.

    Calling this function will override the desired log levels from individual files,
    and if you want to enable a specific level for a specific logger, you'll need
    to get that logger from the loggers dict and call setLevel
    """
    global global_log_level

    if verbose is None and level is None:
        raise ValueError("Must provide one of verbose or level")

    if verbose is not None:
        global_log_level = logging.DEBUG if verbose else logging.INFO

    if level is not None:
        global_log_level = logging.getLevelName(level.upper())

    for logger in loggers.values():
        logger.setLevel(global_log_level)


def get_logger(name: str) -> logging.Logger:
    """
    Gets the logger corresponds to each module
        Parameters:
            name (string): the module name (__name__).

        Returns:
            logger (logging.Logger): the corresponding logger to the given module name.
    """
    dictConfig(logging_module.LOGGING)

    global loggers
    if found_logger := loggers.get(name):
        return found_logger

    logger = logging.getLogger(name)
    loggers[name] = logger
    return logger


def format_loud(target_text: str):
    return f"{BOLD_RED}{target_text}{RESET}"
