#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import tornado
from tornado.websocket import WebSocketHandler
import os
import threading
import uuid
import logging
import json
import time

from mephisto.data_model.architect import Architect
from mephisto.data_model.packet import (
    PACKET_TYPE_ALIVE,
    PACKET_TYPE_NEW_WORKER,
    PACKET_TYPE_NEW_AGENT,
    PACKET_TYPE_AGENT_ACTION,
    PACKET_TYPE_SUBMIT_ONBOARDING,
    PACKET_TYPE_REQUEST_AGENT_STATUS,
)
from typing import List, Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from mephisto.data_model.task import TaskRun
    from mephisto.data_model.database import MephistoDB
    from argparse import _ArgumentGroup as ArgumentGroup

MOCK_DEPLOY_URL = "MOCK_DEPLOY_URL"


def get_rand_id():
    return str(uuid.uuid4())


class SocketHandler(WebSocketHandler):
    def __init__(self, *args, **kwargs):
        self.subs: Dict[int, "SocketHandler"] = kwargs.pop("subs")
        self.app: "MockServer" = kwargs.pop("app")
        self.sid = get_rand_id()
        super().__init__(*args, **kwargs)

    def open(self):
        """
        Opens a websocket and assigns a random UUID that is stored in the class-level
        `subs` variable.
        """
        if self.sid not in self.subs.values():
            self.subs[self.sid] = self

    def on_close(self):
        """
        Runs when a socket is closed.
        """
        del self.subs[self.sid]

    def on_message(self, message_text):
        """
        Callback that runs when a new message is received from a client See the
        chat_service README for the resultant message structure.
        Args:
            message_text: A stringified JSON object with a text or attachment key.
                `text` should contain a string message and `attachment` is a dict.
                See `WebsocketAgent.put_data` for more information about the
                attachment dict structure.
        """
        message = json.loads(message_text)
        if message["packet_type"] == PACKET_TYPE_ALIVE:
            self.app.last_alive_packet = message
        elif message["packet_type"] == PACKET_TYPE_AGENT_ACTION:
            self.app.actions_observed += 1
        elif message["packet_type"] != PACKET_TYPE_REQUEST_AGENT_STATUS:
            self.app.last_packet = message

    def check_origin(self, origin):
        return True


class AliveHandler(tornado.web.RequestHandler):
    """Simple handler for is_alive"""

    def get(self, eids):
        pass  # Default behavior returns 200


class MockServer(tornado.web.Application):
    """
    Tornado-based server that with hooks for sending specific
    messages through socket connections and such
    """

    def __init__(self, port):
        self.subs = {}
        self.port = port
        self.running_instance = None
        self.last_alive_packet: Optional[Dict[str, Any]] = None
        self.actions_observed = 0
        self.last_packet: Optional[Dict[str, Any]] = None
        tornado_settings = {
            "autoescape": None,
            "debug": "/dbg/" in __file__,
            "compiled_template_cache": False,
            "static_url_prefix": "/static/",
            "debug": True,
        }
        handlers = [
            ("/socket", SocketHandler, {"subs": self.subs, "app": self}),
            ("/is_alive", AliveHandler, {}),
        ]
        super(MockServer, self).__init__(handlers, **tornado_settings)

    def __server_thread_fn(self):
        """
        Main loop for the application
        """
        self.running_instance = tornado.ioloop.IOLoop()
        http_server = tornado.httpserver.HTTPServer(self, max_buffer_size=1024 ** 3)
        http_server.listen(self.port)
        self.running_instance.start()
        http_server.stop()

    def _get_sub(self):
        """Return the subscriber socket to write to"""
        return list(self.subs.values())[0]

    def _send_message(self, message):
        """Send the given message back to the mephisto client"""
        socket = self._get_sub()
        message_json = json.dumps(message)
        socket.write_message(message_json)
        time.sleep(0.1)

    def send_agent_act(self, agent_id, act_content):
        """
        Send a packet from the given agent with
        the given content
        """
        self._send_message(
            {
                "packet_type": PACKET_TYPE_AGENT_ACTION,
                "sender_id": agent_id,
                "receiver_id": "Mephisto",
                "data": act_content,
            }
        )

    def register_mock_agent(self, worker_id, agent_details):
        """
        Send a packet asking to register a mock agent.
        """
        self._send_message(
            {
                "packet_type": PACKET_TYPE_NEW_AGENT,
                "sender_id": "MockServer",
                "receiver_id": "Mephisto",
                "data": {
                    "request_id": agent_details,
                    "provider_data": {
                        "worker_id": worker_id,
                        "agent_registration_id": agent_details,
                    },
                },
            }
        )

    def register_mock_agent_after_onboarding(
        self, worker_id, agent_details, onboard_data
    ):
        """
        Send a packet asking to register a mock agent.
        """
        self._send_message(
            {
                "packet_type": PACKET_TYPE_SUBMIT_ONBOARDING,
                "sender_id": "MockServer",
                "receiver_id": "Mephisto",
                "data": {
                    "request_id": agent_details,
                    "provider_data": {
                        "worker_id": worker_id,
                        "agent_registration_id": agent_details,
                    },
                    "onboard_data": onboard_data,
                },
            }
        )

    def register_mock_worker(self, worker_name):
        """
        send a packet asking to register a mock worker.
        """
        self._send_message(
            {
                "packet_type": PACKET_TYPE_NEW_WORKER,
                "sender_id": "MockServer",
                "receiver_id": "Mephisto",
                "data": {
                    "request_id": worker_name,
                    "provider_data": {"worker_name": worker_name},
                },
            }
        )

    def disconnect_mock_agent(self, agent_id):
        """
        Mark a mock agent as disconnected.
        """
        # TODO implement when handling disconnections
        pass

    def launch_mock(self):
        """
        Start the primary loop for this application
        """
        self.__server_thread = threading.Thread(target=self.__server_thread_fn)
        self.__server_thread.start()

    def shutdown_mock(self):
        """
        Defined to shutown the tornado application.
        """

        def stop_and_free():
            self.running_instance.stop()

        self.running_instance.add_callback(stop_and_free)
        self.__server_thread.join()


class MockArchitect(Architect):
    """
    The MockArchitect runs a mock server on the localhost so that
    we can send special packets and assert connections have been made
    """

    def __init__(
        self,
        db: "MephistoDB",
        opts: Dict[str, Any],
        task_run: "TaskRun",
        build_dir_root: str,
    ):
        """Create an architect for use in testing"""
        self.task_run = task_run
        self.build_dir = build_dir_root
        self.task_run_id = task_run.db_id
        self.should_run_server = opts.get("should_run_server")
        self.port = opts.get("port")
        self.server: Optional["MockServer"] = None
        # TODO track state in parent class?
        self.prepared = False
        self.deployed = False
        self.cleaned = False
        self.did_shutdown = False

    @classmethod
    def add_args_to_group(cls, group: "ArgumentGroup") -> None:
        """
        MockArchitects can be configured to launch a mock server
        """
        super(MockArchitect, cls).add_args_to_group(group)

        group.description = """
            MockArchitect: Mock Architects can be configured to 
            launch a mock server on a localhost port.
        """
        group.add_argument(
            "--should-run-server",
            dest="should_run_server",
            help="Whether a mock server should be launched",
            default=False,
            type=bool,
        )
        group.add_argument(
            "--port", dest="port", help="Port to launch the server on", default="3000"
        )
        return

    def get_socket_urls(self) -> List[str]:
        """Return the path to the local server socket"""
        assert self.port is not None, "No ports for socket"
        return [f"ws://localhost:{self.port}/socket"]

    def download_file(self, target_filename: str, save_dir: str) -> None:
        """
        Mock architects can just pretend to write a file
        """
        with open(os.path.join(save_dir, target_filename), "wb") as fp:
            fp.write("mock")

    def prepare(self) -> str:
        """Mark the preparation call"""
        self.prepared = True
        built_dir = os.path.join(
            self.build_dir, "mock_build_{}".format(self.task_run_id)
        )
        os.makedirs(built_dir)
        return built_dir

    def deploy(self) -> str:
        """Mock a deploy or deploy a mock server, depending on settings"""
        self.deployed = True
        if not self.should_run_server:
            return MOCK_DEPLOY_URL
        else:
            self.server = MockServer(self.port)
            self.server.launch_mock()
            return f"http://localhost:{self.port}/"

    def cleanup(self) -> None:
        """Mark the cleanup call"""
        self.cleaned = True

    def shutdown(self) -> None:
        """Mark the shutdown call"""
        self.did_shutdown = True
        if self.should_run_server and self.server is not None:
            self.server.shutdown_mock()
