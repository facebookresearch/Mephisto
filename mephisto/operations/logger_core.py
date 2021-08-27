#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import logging
from typing import Optional, Dict

loggers: Dict[str, logging.Logger] = {}
global_log_level = logging.INFO


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

    global loggers
    if loggers.get(name):
        return loggers.get(name)
    else:
        logger = logging.getLogger(name)

        level_dict = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL,
        }

        if level is not None:
            logger.setLevel(level_dict[level.lower()])
        elif verbose is not None:
            logger.setLevel(logging.DEBUG if verbose else logging.INFO)
        else:
            logger.setLevel(global_log_level)
        if log_file is None:
            handler = logging.StreamHandler()
        else:
            handler = logging.RotatingFileHandler(log_file)
        # TODO revisit logging handlers after deciding whether or not to just use
        # Hydra default?
        # formatter = logging.Formatter(
        #     "[%(asctime)s] p%(process)s {%(filename)s:%(lineno)d} %(levelname)5s - %(message)s",
        #     "%m-%d %H:%M:%S",
        # )

        # handler.setFormatter(formatter)
        # logger.addHandler(handler)
        loggers[name] = logger
        return logger
