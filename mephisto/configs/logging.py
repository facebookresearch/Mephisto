#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
CONSOLE_LOG_LEVEL = os.environ.get("CONSOLE_LOG_LEVEL", "INFO")

_now = datetime.now()
date_string = _now.strftime("%Y-%m-%d")
time_string = _now.strftime("%H-%M-%S")
executed_filename = os.path.splitext(os.path.basename(sys.argv[0]))[0]

# Create dirs recursivelly if they do not exist
os.makedirs(os.path.join(BASE_DIR, "outputs", date_string, time_string), exist_ok=True)

# Logging
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
            "level": CONSOLE_LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": os.path.join(
                BASE_DIR, "outputs", date_string, time_string, f'{executed_filename}.log',
            ),
            "formatter": "default",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "propagate": True,
            "level": CONSOLE_LOG_LEVEL,
        },
    },
}
