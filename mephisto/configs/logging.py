#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
WRITE_LOG_TO_FILE = os.environ.get("WRITE_LOG_TO_FILE", "0")

_now = datetime.now()
date_string = _now.strftime("%Y-%m-%d")
time_string = _now.strftime("%H-%M-%S")


def get_log_handlers():
    """We enable module-level loggers via env variable (that we can set in the console),
    so that hydra doesn't create an empty file for every module-level logger
    """
    handlers = ["console"]
    if WRITE_LOG_TO_FILE == "1":
        handlers.append("file")
        # Create dirs recursivelly if they do not exist
        os.makedirs(os.path.join(BASE_DIR, "outputs", date_string, time_string), exist_ok=True)
    return handlers


def get_log_filename():
    """Compose logfile path formatted same way as hydra"""
    executed_filename = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    return os.path.join(
        BASE_DIR,
        "outputs",
        date_string,
        time_string,
        f"{executed_filename}.log",
    )


log_handlers = get_log_handlers()
log_filename = get_log_filename()

# Logging config
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        **(
            {
                "file": {
                    "level": LOG_LEVEL,
                    "class": "logging.FileHandler",
                    "filename": log_filename,
                    "formatter": "default",
                }
            }
            if "file" in log_handlers
            else {}
        ),
    },
    "loggers": {
        "": {
            "handlers": log_handlers,
            "propagate": True,
            "level": LOG_LEVEL,
        },
    },
}
