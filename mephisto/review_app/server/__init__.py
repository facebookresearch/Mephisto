#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import os
import traceback
from logging.config import dictConfig
from pathlib import Path
from typing import Optional
from typing import Tuple

from flask import Flask
from flask_cors import CORS
from werkzeug import Response
from werkzeug.exceptions import HTTPException as WerkzeugHTTPException
from werkzeug.utils import import_string

from mephisto.abstractions.database import EntryDoesNotExistException
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.abstractions.providers.prolific.api import status
from mephisto.abstractions.providers.prolific.api.exceptions import ProlificException
from mephisto.tools.data_browser import DataBrowser
from mephisto.utils.logger_core import get_logger
from .urls import init_urls

FLASK_SETTINGS_MODULE = os.environ.get(
    "FLASK_SETTINGS_MODULE",
    "mephisto.review_app.server.settings.base",
)


def create_app(debug: bool = False, database_path: Optional[str] = None) -> Flask:
    # Logging
    # TODO(#1058): [Review APP] Fix logging (it works in views only with `app.logger` somehow)
    flask_logger = get_logger("")
    settings = import_string(FLASK_SETTINGS_MODULE)
    dictConfig(settings.LOGGING)

    # Create and configure the app
    static_folder = os.path.join(
        Path(__file__).resolve().parent.parent,
        "client",
        "build",
        "static",
    )
    app = Flask(__name__, static_folder=static_folder, static_url_path="/static")
    CORS(app)

    # Debug
    app.debug = debug

    # Logger
    app.logger = flask_logger

    # Settings
    app.config.from_object(FLASK_SETTINGS_MODULE)

    # Databases
    app.db = LocalMephistoDB(database_path=database_path)
    app.data_browser = DataBrowser(db=app.db)

    # API URLS
    init_urls(app)

    # Logger for this module
    logger = get_logger(name=__name__)

    # Exceptions handlers
    @app.errorhandler(WerkzeugHTTPException)
    def handle_flask_exception(e: WerkzeugHTTPException) -> Response:
        logger.error("".join(traceback.format_tb(e.__traceback__)))
        response = e.get_response()
        response.data = json.dumps(
            {
                "error": e.description,
            }
        )
        response.content_type = "application/json"
        return response

    @app.errorhandler(Exception)
    def handle_not_flask_exception(e: Exception) -> Tuple[dict, int]:
        # Not to handle Flask exceptions here, pass it further to catch in `handle_flask_exception`
        if isinstance(e, WerkzeugHTTPException):
            return e

        elif isinstance(e, ProlificException):
            logger.exception("Prolific error")
            return {
                "error": e.message,
            }, status.HTTP_400_BAD_REQUEST

        elif isinstance(e, EntryDoesNotExistException):
            return {
                "error": "Not found",
            }, status.HTTP_404_NOT_FOUND

        # Other uncaught exceptions
        logger.error("".join(traceback.format_tb(e.__traceback__)))
        return {
            "error": f"Server error: {e}",
        }, status.HTTP_500_INTERNAL_SERVER_ERROR

    return app
