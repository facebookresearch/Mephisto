#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import logging
from typing import Optional

loggers = {}


def get_logger(
    name: str, 
    verbose: bool = False, 
    log_file: Optional[str] = None, 
    level: Optional[str] = None,
) -> logging.Logger:
    """
    Gets the logger corresponds to each module. For a specific logger `name`:
    - setting `verbose` will output DEBUG information and will override `level` settings.
    - setting `level` will specify a specific logging level, defaults to info
    - setting `log_file` will output the logs to the specified file, defaults to stdout
    """

    global loggers
    if loggers.get(name):
        return loggers.get(name)
    else:
        logger = logging.getLogger(name)

        if verbose:
            logger.setLevel(logging.DEBUG)
        elif level is not None:
            level_dict = {
                "info": logging.INFO,
                "debug": logging.DEBUG,
                "warning": logging.WARNING,
                "error": logging.ERROR,
                "critical": logging.CRITICAL,
            }
            logger.setLevel(level_dict[level.lower()])
        else:
            logger.setLevel(logging.INFO)
        if log_file is None:
            handler = logging.StreamHandler()
        else:
            handler = logging.RotatingFileHandler(log_file)
        formatter = logging.Formatter(
            "[%(asctime)s] p%(process)s {%(filename)s:%(lineno)d} %(levelname)5s - %(message)s",
            "%m-%d %H:%M:%S",
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)
        loggers[name] = logger
        return logger
