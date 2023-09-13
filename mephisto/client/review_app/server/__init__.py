#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import os
import traceback
from logging.config import dictConfig
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
    'FLASK_SETTINGS_MODULE',
    'mephisto.client.review_app.server.settings.base',
)


def create_app(provider: str, debug: bool) -> Flask:
    # Logging
    # TODO [Review APP]: Fix logging (it works in views only with `app.logger` somehow)
    flask_logger = get_logger('')
    settings = import_string(FLASK_SETTINGS_MODULE)
    dictConfig(settings.LOGGING)

    # Create and configure the app
    app = Flask(__name__)
    CORS(app)

    # Debug
    app.debug = debug

    # Logger
    app.logger = flask_logger

    # Settings
    app.config.from_object(FLASK_SETTINGS_MODULE)

    # Databases
    app.db = LocalMephistoDB()
    app.data_browser = DataBrowser(db=app.db)
    app.datastore = app.db.get_datastore_for_provider(provider)

    # API URLS
    init_urls(app)

    # Logger for this module
    logger = get_logger(name=__name__)

    # Exceptions handlers
    @app.errorhandler(WerkzeugHTTPException)
    def handle_flask_exception(e: WerkzeugHTTPException) -> Response:
        logger.error(''.join(traceback.format_tb(e.__traceback__)))
        response = e.get_response()
        response.data = json.dumps({
            'error': e.description,
        })
        response.content_type = 'application/json'
        return response

    @app.errorhandler(Exception)
    def handle_not_flask_exception(e: Exception) -> Tuple[dict, int]:
        # Not to handle Flask exceptions here, pass it further to catch in `handle_flask_exception`
        if isinstance(e, WerkzeugHTTPException):
            return e

        elif isinstance(e, ProlificException):
            logger.exception('Prolific error')
            return {
                'error': e.message,
            }, status.HTTP_400_BAD_REQUEST

        elif isinstance(e, EntryDoesNotExistException):
            return {
                'error': 'Not found',
            }, status.HTTP_404_NOT_FOUND

        # Other uncaught exceptions
        logger.error(''.join(traceback.format_tb(e.__traceback__)))
        return {
            'error': str(e),
        }, status.HTTP_500_INTERNAL_SERVER_ERROR

    return app
