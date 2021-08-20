#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Callable, Optional
from mephisto.data_model.packet import Packet
from mephisto.abstractions.channel import Channel, STATUS_CHECK_TIME

import errno
import websocket
import threading
import json
import time

from mephisto.operations.logger_core import get_logger

logger = get_logger(name=__name__)


class WebsocketChannel(Channel):
    """
    Channel for communicating with a server via websockets.
    """

    def __init__(
        self,
        channel_id: str,
        on_channel_open: Callable[[str], None],
        on_catastrophic_disconnect: Callable[[str], None],
        on_message: Callable[[str, Packet], None],
        socket_url: str,
    ):
        """
        Create a channel by the given name, and initialize any resources that
        will later be required during the `open` call.

        Requires a socket_url to connect with.
        """
        super().__init__(
            channel_id=channel_id,
            on_channel_open=on_channel_open,
            on_catastrophic_disconnect=on_catastrophic_disconnect,
            on_message=on_message,
        )
        self.socket_url = socket_url
        self.socket: Optional[websocket.WebSocketApp] = None
        self.thread: Optional[threading.Thread] = None
        self._is_alive = False
        self._is_closed = False

    def is_closed(self):
        """
        Return whether or not this connection has been explicitly closed
        by the supervisor or another source.
        """
        return self._is_closed

    def close(self):
        """
        Close this channel, and ensure that all threads and surrounding
        resources are cleaned up
        """
        self._is_closed = True
        try:
            self.socket.close()
        except Exception:
            # socket already closed
            pass
        self._is_alive = False
        if self.thread is not None:
            self.thread.join()

    def is_alive(self):
        """Return if this channel is actively able to send/recieve messages."""
        return self._is_alive

    def open(self):
        """Set up a socket handling thread."""

        def on_socket_open(*args):
            self._is_alive = True
            self.on_channel_open(self.channel_id)
            logger.info(f"channel open {args}")

        def on_error(ws, error):
            if hasattr(error, "errno"):
                if error.errno == errno.ECONNREFUSED:
                    # TODO(CLEAN) replace with channel exception
                    raise Exception(
                        f"Socket {self.socket_url} refused connection, cancelling"
                    )
            else:
                logger.error(f"Socket logged error: {error}")
                if isinstance(error, websocket._exceptions.WebSocketException):
                    return

                import traceback

                traceback.print_exc()
                try:
                    # Close the socket to attempt to reconnect
                    self.socket.close()
                    self.socket.keep_running = False
                except Exception:
                    # TODO(CLEAN) only catch socket closed connection
                    # Already closed
                    pass

        def on_disconnect(*args):
            """Disconnect event is a no-op for us, as the server reconnects
            automatically on a retry.
            """
            # TODO(OWN) we need to set a timeout for reconnecting to the server,
            # if it fails it's time to call on_catastrophic_disconnect
            pass

        def on_message(*args):
            """Incoming message handler defers to the internal handler"""
            try:
                packet_dict = json.loads(args[1])
                packet = Packet.from_dict(packet_dict)
                self.on_message(self.channel_id, packet)
            except Exception as e:
                # TODO(CLEAN) properly handle only failed from_dict calls
                logger.exception(repr(e), exc_info=True)
                raise

        def run_socket(*args):
            while not self._is_closed:
                try:
                    socket = websocket.WebSocketApp(
                        self.socket_url,
                        on_message=on_message,
                        on_error=on_error,
                        on_close=on_disconnect,
                    )
                    self.socket = socket
                    socket.on_open = on_socket_open
                    socket.run_forever(ping_interval=8 * STATUS_CHECK_TIME)
                except Exception as e:
                    logger.exception(
                        f"Socket error {repr(e)}, attempting restart", exc_info=True
                    )
                time.sleep(0.2)

        # Start listening thread
        self.thread = threading.Thread(
            target=run_socket, name=f"socket-thread-{self.socket_url}"
        )
        self.thread.start()

    def send(self, packet: "Packet") -> bool:
        """
        Send the packet given to the intended recipient.
        Return True on success and False on failure.
        """
        if self.socket is None:
            return False
        try:
            data = packet.to_sendable_dict()
            self.socket.send(json.dumps(data))
        except websocket.WebSocketConnectionClosedException:
            # The channel died mid-send, wait for it to come back up
            return False
        except BrokenPipeError:
            # The channel died mid-send, wait for it to come back up
            return False
        except Exception as e:
            logger.exception(
                f"Unexpected socket error occured: {repr(e)}", exc_info=True
            )
            return False
        return True
