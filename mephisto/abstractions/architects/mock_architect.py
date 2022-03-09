#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import tornado
from tornado.websocket import WebSocketHandler
import os
import threading
import uuid
import json
import time

from mephisto.abstractions.architect import Architect, ArchitectArgs
from dataclasses import dataclass, field
from mephisto.abstractions.blueprint import AgentState
from mephisto.data_model.packet import (
    PACKET_TYPE_ALIVE,
    PACKET_TYPE_SUBMIT_ONBOARDING,
    PACKET_TYPE_SUBMIT_UNIT,
    PACKET_TYPE_CLIENT_BOUND_LIVE_UPDATE,
    PACKET_TYPE_MEPHISTO_BOUND_LIVE_UPDATE,
    PACKET_TYPE_REGISTER_AGENT,
    PACKET_TYPE_AGENT_DETAILS,
    PACKET_TYPE_UPDATE_STATUS,
    PACKET_TYPE_REQUEST_STATUSES,
    PACKET_TYPE_RETURN_STATUSES,
    PACKET_TYPE_ERROR,
)
from mephisto.operations.registry import register_mephisto_abstraction
from mephisto.abstractions.architects.channels.websocket_channel import WebsocketChannel
from typing import List, Dict, Any, Optional, TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from mephisto.abstractions._subcomponents.channel import Channel
    from mephisto.data_model.packet import Packet
    from mephisto.data_model.task_run import TaskRun
    from mephisto.abstractions.database import MephistoDB
    from argparse import _ArgumentGroup as ArgumentGroup
    from omegaconf import DictConfig
    from mephisto.abstractions.blueprint import SharedTaskState

MOCK_DEPLOY_URL = "MOCK_DEPLOY_URL"
ARCHITECT_TYPE = "mock"


def get_rand_id():
    return str(uuid.uuid4())


@dataclass
class MockArchitectArgs(ArchitectArgs):
    """Additional arguments for configuring a mock architect"""

    _architect_type: str = ARCHITECT_TYPE
    should_run_server: bool = field(
        default=False, metadata={"help": "Addressible location of the server"}
    )
    port: str = field(default="3000", metadata={"help": "Port to launch the server on"})


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
        elif message["packet_type"] == PACKET_TYPE_CLIENT_BOUND_LIVE_UPDATE:
            self.app.actions_observed += 1
        elif message["packet_type"] == PACKET_TYPE_MEPHISTO_BOUND_LIVE_UPDATE:
            self.app.actions_observed += 1
        elif message["packet_type"] != PACKET_TYPE_REQUEST_STATUSES:
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
        http_server = tornado.httpserver.HTTPServer(self, max_buffer_size=1024**3)
        http_server.listen(self.port)
        self.running_instance.start()
        http_server.stop()

    def _get_sub(self):
        """Return the subscriber socket to write to"""
        return list(self.subs.values())[0]

    def _send_message(self, message):
        """Send the given message back to the mephisto client"""
        failed_attempts = 0
        last_exception = None
        while failed_attempts < 5:
            try:
                socket = self._get_sub()
                message_json = json.dumps(message)
                socket.write_message(message_json)
                last_exception = None
                break
            except Exception as e:
                last_exception = e
                time.sleep(0.2)
                failed_attempts += 1
            finally:
                time.sleep(0.1)
        if last_exception is not None:
            raise last_exception

    def send_agent_act(self, agent_id, act_content):
        """
        Send a packet from the given agent with
        the given content
        """
        self._send_message(
            {
                "packet_type": PACKET_TYPE_MEPHISTO_BOUND_LIVE_UPDATE,
                "subject_id": agent_id,
                "data": act_content,
            }
        )

    def register_mock_agent(self, worker_name, agent_details):
        """
        Send a packet asking to register a mock agent.
        """
        self._send_message(
            {
                "packet_type": PACKET_TYPE_REGISTER_AGENT,
                "subject_id": "MockServer",
                "data": {
                    "request_id": agent_details,
                    "provider_data": {
                        "worker_name": worker_name,
                        "agent_registration_id": agent_details,
                    },
                },
            }
        )

    def submit_mock_unit(self, agent_id, submit_data):
        """
        Send a packet asking to submit data.
        """
        self._send_message(
            {
                "packet_type": PACKET_TYPE_SUBMIT_UNIT,
                "subject_id": agent_id,
                "data": submit_data,
            }
        )

    def register_mock_agent_after_onboarding(self, worker_id, agent_id, onboard_data):
        """
        Send a packet asking to register a mock agent.
        """
        self._send_message(
            {
                "packet_type": PACKET_TYPE_SUBMIT_ONBOARDING,
                "subject_id": agent_id,
                "data": {
                    "request_id": "1234",
                    "onboarding_data": onboard_data,
                },
            }
        )

    def disconnect_mock_agent(self, agent_id):
        """
        Mark a mock agent as disconnected.
        """
        self._send_message(
            {
                "packet_type": PACKET_TYPE_RETURN_STATUSES,
                "subject_id": "Mephisto",
                "data": {agent_id: AgentState.STATUS_DISCONNECT},
            }
        )

    def launch_mock(self):
        """
        Start the primary loop for this application
        """
        self.__server_thread = threading.Thread(
            target=self.__server_thread_fn, name="mock-server-thread"
        )
        self.__server_thread.start()

    def shutdown_mock(self):
        """
        Defined to shutown the tornado application.
        """

        def stop_and_free():
            self.running_instance.stop()

        self.running_instance.add_callback(stop_and_free)
        self.__server_thread.join()


@register_mephisto_abstraction()
class MockArchitect(Architect):
    """
    The MockArchitect runs a mock server on the localhost so that
    we can send special packets and assert connections have been made
    """

    ArgsClass = MockArchitectArgs
    ARCHITECT_TYPE = ARCHITECT_TYPE

    def __init__(
        self,
        db: "MephistoDB",
        args: "DictConfig",
        shared_state: "SharedTaskState",
        task_run: "TaskRun",
        build_dir_root: str,
    ):
        """Create an architect for use in testing"""
        self.task_run = task_run
        self.build_dir = build_dir_root
        self.task_run_id = task_run.db_id
        self.should_run_server = args.architect.should_run_server
        self.port = args.architect.port
        self.server: Optional["MockServer"] = None
        # TODO(#651) track state in parent class?
        self.prepared = False
        self.deployed = False
        self.cleaned = False
        self.did_shutdown = False

    def _get_socket_urls(self) -> List[str]:
        """Return the path to the local server socket"""
        assert self.port is not None, "No ports for socket"
        return [f"ws://localhost:{self.port}/socket"]

    def get_channels(
        self,
        on_channel_open: Callable[[str], None],
        on_catastrophic_disconnect: Callable[[str], None],
        on_message: Callable[[str, "Packet"], None],
    ) -> List["Channel"]:
        """
        Return a list of all relevant channels that the ClientIOHandler
        will need to register to in order to function
        """
        urls = self._get_socket_urls()
        return [
            WebsocketChannel(
                f"mock_channel_{self.task_run_id}_{idx}",
                on_channel_open=on_channel_open,
                on_catastrophic_disconnect=on_catastrophic_disconnect,
                on_message=on_message,
                socket_url=url,
            )
            for idx, url in enumerate(urls)
        ]

    def download_file(self, target_filename: str, save_dir: str) -> None:
        """
        Mock architects can just pretend to write a file
        """
        with open(os.path.join(save_dir, target_filename), "wb") as fp:
            fp.write(b"mock\n")

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
