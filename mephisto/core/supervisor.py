#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import errno
import logging
import json
import threading
import time
from queue import PriorityQueue, Empty
import websocket
import time
from mephisto.data_model.packet import (
    Packet,
    PACKET_TYPE_ALIVE,
    PACKET_TYPE_AGENT_ACTION,
    PACKET_TYPE_NEW_AGENT,
    PACKET_TYPE_NEW_WORKER,
    PACKET_TYPE_REQUEST_AGENT_STATUS,
    PACKET_TYPE_RETURN_AGENT_STATUS,
    PACKET_TYPE_INIT_DATA,
)

from typing import Dict, Optional, List, Any, TYPE_CHECKING
if TYPE_CHECKING:
    from mephisto.data_model.agent import Agent
    from mephisto.data_model.database import MephistoDB

# TODO this class manages communications between the server
# and workers, ensures that their status is properly tracked,
# and also provides some helping utility functions for
# groups of workers or worker/agent compatibility.

# Mostly, the supervisor babysits the socket and the workers

SYSTEM_SOCKET_ID = 'mephisto'  # TODO pull from somewhere
SERVER_SOCKET_ID = 'server' # TODO pull from somewhere
STATUS_CHECK_TIME = 10
START_DEATH_TIME = 10

class Supervisor:

    def __init__(self, db: MephistoDB):
        self.db = db
        self.active_agents: Dict[str, "Agent"] = {}
        self.agent_mappings: Dict[str, str] = {}
        self.sockets: Dict[str, websocket.WebSocketApp] = {}
        self.socket_threads: Dict[str, threading.Thread] = {}
        self.live_sockets: Dict[str, bool]
        self.responses: Dict[str, Dict[str, Any]] = {}
        self.last_status_check = time.time()

    def setup_socket(self, url: str):
        """Set up a socket communicating with the server at the given url"""
        # Clear responses, as we won't have one for this server
        self.responses = {}
        self.live_sockets[url] = False

        def on_socket_open(*args):
            self.live_sockets[url] = True
            self._send_alive(self.sockets[url])
            # TODO use logger?
            print(f'socket open {args}')

        def on_error(ws, error):
            if error.errno == errno.ECONNREFUSED:
                raise Exception(f"Socket {url} refused connection, cancelling")
            else:
                print(f'Socket logged error: {error}')
                try:
                    ws.close()
                except Exception:
                    # Already closed
                    pass

        def on_disconnect(*args):
            """Disconnect event is a no-op for us, as the server reconnects
            automatically on a retry.
            """
            # TODO we need to set a timeout for reconnecting to the server
            pass

        def on_message(*args):
            """Incoming message handler defers to the internal handler
            """
            packet_dict = json.loads(args[1])
            packet = Packet.from_dict(packet_dict)
            self._on_message(packet, url)

        def run_socket(*args):
            url_base_name = url.split('https://')[1]
            protocol = "wss"
            if url_base_name in ['localhost', '127.0.0.1']:
                protocol = "ws"
            while url in self.sockets:
                try:
                    sock_addr = "{}://{}:{}/".format(protocol, url_base_name, self.port)
                    self.sockets[url] = websocket.WebSocketApp(
                        sock_addr,
                        on_message=on_message,
                        on_error=on_error,
                        on_close=on_disconnect,
                    )
                    self.sockets[url].on_open = on_socket_open
                    self.sockets[url].run_forever(ping_interval=8 * self.STATUS_CHECK_TIME)
                except Exception as e:
                    shared_utils.print_and_log(
                        logging.WARN,
                        'Socket error {}, attempting restart'.format(repr(e)),
                    )
                time.sleep(0.2)

        # Start listening thread
        self.socket_threads[url] = threading.Thread(
            target=run_socket, name=f'socket-thread-{url}'
        )
        self.socket_threads[url].start()
        start_time = time.time()
        while not self.live_sockets[url]:
            if time.time() - start_time > START_DEATH_TIME:
                # TODO better handle failing to connect with the server
                raise ConnectionRefusedError(  # noqa F821 we only support py3
                    'Was not able to establish a connection with the server, '
                    'please try to run again. If that fails,'
                    'please ensure that your local device has the correct SSL '
                    'certs installed.'
                )
            try:
                self._send_alive(self.sockets[url])
            except Exception:
                pass
            time.sleep(0.3)

    def _send_through_socket(self, socket: websocket.WebSocketApp, packet: Packet) -> bool:
        """Send a packet through the socket, handle any errors"""
        if socket is None:
            return False
        try:
            data = packet.to_sendable_dict()
            socket.send(data)
        except websocket.WebSocketConnectionClosedException:
            # The channel died mid-send, wait for it to come back up
            return False
        except BrokenPipeError:
            # The channel died mid-send, wait for it to come back up
            return False
        except Exception as e:
            print('Unexpected socket error occured: {}'.format(repr(e)))
            return False
        return True

    def _send_alive(self, socket) -> bool:
        return self._send_through_socket(socket, Packet(
            packet_type=PACKET_TYPE_ALIVE,
            sender_id=SYSTEM_SOCKET_ID,
            receiver_id=SERVER_SOCKET_ID,
        ))

    def _on_act(self, packet: Packet):
        """Handle an action as sent from an agent"""
        agent = self.active_agents[packet.sender_id]
        agent.pending_actions.append(packet)
        agent.has_action.set()

    def _on_message(self, packet: Packet, url: str):
        """Handle incoming messages from the socket"""
        if packet.type == PACKET_TYPE_AGENT_ACTION:
            self._on_act(packet)
        elif packet.type == PACKET_TYPE_NEW_AGENT:
            # TODO talk to the crowd_provider
            # listed in this packet
            pass
        elif packet.type == PACKET_TYPE_NEW_WORKER:
            # TODO talk to the crowd_provider
            # listed in this packet
            pass
        elif packet.type == PACKET_TYPE_RETURN_AGENT_STATUS:
            # Record this status response
            self.responses[url] = packet.data
        else:
            # PACKET_TYPE_REQUEST_AGENT_STATUS, PACKET_TYPE_ALIVE,
            # PACKET_TYPE_INIT_DATA
            raise Exception(f"Unexpected packet type {packet.type}")

    def _try_send_agent_messages(self, agent: "Agent"):
        """Handle sending any possible messages for a specific agent"""
        agent_socket_url = self.agent_mappings[agent.db_id]
        socket = self.sockets[agent_socket_url]
        while len(agent.pending_observations) > 0:
            curr_obs = agent.pending_observations.pop(0)
            did_send = self._send_through_socket(socket, curr_obs)
            if not did_send:
                print(f'Failed to send packet {curr_obs} to {agent_socket_url}')
                return  # something up with the socket, try later

    def _handle_updated_agent_status(self, status_map: Dict[str, str]):
        """
        Handle updating the local statuses for agents based on
        the previously reported agent statuses.

        Takes as input a mapping from agent_id to server-side status
        """
        # TODO implement
        pass

    def _request_status_update(self) -> None:
        """
        Check last round of statuses, then request
        an update from the server on all agent's current status
        """
        if time.time() - self.last_status_check < STATUS_CHECK_TIME:
            return

        # If there are responses to check
        if len(self.responses) != 0:
            found_statuses: Dict[str, str] = {}
            for url, status_map in self.responses.items():
                if status_map is None:
                    # TODO handle what appears to be a broken socket
                    raise Exception("Socket broken, what do?")
                found_statuses.update(status_map)
            self._handle_updated_agent_status(found_statuses)

        for url, socket in self.sockets.items():
            send_packet = Packet(
                packet_type=PACKET_TYPE_REQUEST_AGENT_STATUS,
                sender_id=SYSTEM_SOCKET_ID,
                receiver_id=SERVER_SOCKET_ID,
                data={},
            )
            self._send_through_socket(socket, send_packet)

    def socket_handling_thread(self) -> None:
        """Thread for handling outgoing messages to the socket"""
        for agent in self.active_agents.values():
            self._try_send_agent_messages(agent)
        self._request_status_update()
        # TODO is there a way we can trigger this when
        # agents observe instead?
        time.sleep(0.1)
