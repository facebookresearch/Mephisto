#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import logging
from logging.handlers import RotatingFileHandler
from typing import Any, List, Optional, Dict, Set
from rich.logging import RichHandler
from mephisto.utils.rich import console

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
        logging.warn(msg)


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


def get_logger(
    name: str,
    verbose: Optional[bool] = None,
    log_file: Optional[str] = None,
    level: Optional[str] = None,
) -> logging.Logger:
    """
    Gets the logger corresponds to each module
            Parameters:
                    name (string): the module name (__name__).
                    verbose (bool): INFO level activated if True.
                    log_file (string): path for saving logs locally.
                    level (string): logging level. Values options: [info, debug, warning, error, critical].

            Returns:
                    logger (logging.Logger): the corresponding logger to the given module name.
    """
    LOGFORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOGFORMAT_RICH = "%(message)s"
    global loggers
    found_logger = loggers.get(name)
    if found_logger is not None:
        return found_logger
    else:

        level_dict = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL,
        }
        ch = RichHandler()
        ch.setFormatter(logging.Formatter(LOGFORMAT_RICH))
        logging_format: List[Any] = [ch]
        if log_file is not None:
            logging_format.append(RotatingFileHandler(log_file))
        logging.basicConfig(
            level=level_dict[level.lower()] if level is not None else logging.INFO,
            format=LOGFORMAT,
            handlers=logging_format,
        )

        logger = logging.getLogger(name)

        logger.addHandler(ch)

        if level is not None:
            logger.setLevel(level_dict[level.lower()])
        elif verbose is not None:
            logger.setLevel(logging.DEBUG if verbose else logging.INFO)
        else:
            logger.setLevel(global_log_level)

        loggers[name] = logger
        return logger


BOLD_RED = "\u001b[31;1m"
RESET = "\u001b[0m"


def format_loud(target_text: str):
    return f"{BOLD_RED}{target_text}{RESET}"
