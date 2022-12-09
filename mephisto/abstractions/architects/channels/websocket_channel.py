#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Callable, Optional, TYPE_CHECKING
from mephisto.data_model.packet import Packet
from mephisto.operations.datatypes import LoopWrapper
from mephisto.abstractions._subcomponents.channel import Channel, STATUS_CHECK_TIME

import errno
import websockets
import threading
import json
import time
import asyncio

if TYPE_CHECKING:
    from websockets.client import WebSocketClientProtocol

from mephisto.utils.logger_core import get_logger

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
        self.socket: Optional["WebSocketClientProtocol"] = None
        self.thread: Optional[threading.Thread] = None
        self._is_alive = False
        self._is_closed = False
        self._socket_task: Optional[asyncio.Task] = None

    def is_closed(self):
        """
        Return whether or not this connection has been explicitly closed
        by the ClientIOHandler or another source.
        """
        return self._is_closed

    def close(self):
        """
        Close this channel, and ensure that all threads and surrounding
        resources are cleaned up
        """
        self._is_closed = True

        target_loop = self.loop_wrap.loop
        target_loop.call_soon_threadsafe(target_loop.stop)

        self._is_alive = False
        if self.thread is not None:
            self.thread.join()

    def is_alive(self):
        """Return if this channel is actively able to send/recieve messages."""
        return self._is_alive

    def open(self):
        """Set up a socket handling thread."""

        def on_socket_open():
            self._is_alive = True
            self.on_channel_open(self.channel_id)
            logger.info(f"channel open")

        async def on_error(error):
            if self._is_closed:
                return  # Don't do anything if we're already closed
            if hasattr(error, "errno"):
                if error.errno == errno.ECONNREFUSED:
                    # TODO(CLEAN) replace with channel exception
                    raise Exception(
                        f"Socket {self.socket_url} refused connection, cancelling"
                    )
            else:
                logger.info(f"Socket logged error: {error}")

                import traceback

                traceback.print_exc()
                try:
                    # Close the socket to attempt to reconnect
                    await self.socket.close()
                except Exception:
                    # TODO(CLEAN) only catch socket closed connection
                    # Already closed
                    pass

        def on_message(msg_json):
            """Incoming message handler defers to the internal handler"""
            try:
                packet_dict = json.loads(msg_json)
                packet = Packet.from_dict(packet_dict)
                self.on_message(self.channel_id, packet)
            except Exception as e:
                # TODO(CLEAN) properly handle only failed from_dict calls
                logger.exception(repr(e), exc_info=True)
                raise

        async def run_socket():
            loop = asyncio.get_running_loop()

            # Outer loop allows reconnects
            while not self._is_closed:
                try:
                    async with websockets.connect(
                        self.socket_url, open_timeout=30
                    ) as websocket:
                        # Inner loop recieves messages until closed
                        self.socket = websocket
                        on_socket_open()
                        try:
                            while not self._is_closed:
                                message = await websocket.recv()
                                on_message(message)
                        except websockets.exceptions.ConnectionClosedOK:
                            pass
                        except websockets.exceptions.ConnectionClosedError as e:
                            if isinstance(e.__cause__, asyncio.CancelledError):
                                pass
                            else:
                                await on_error(e)
                        except Exception as e:
                            logger.exception(
                                f"Socket error {repr(e)}, attempting restart",
                                exc_info=True,
                            )
                        await asyncio.sleep(0.2)
                except asyncio.TimeoutError:
                    # Issue with opening this channel, should shut down to prevent inaccessible tasks
                    self.on_catastrophic_disconnect(self.channel_id)
                    return
                except OSError as e:
                    logger.error(
                        f"Unhandled OSError exception in socket {e}, attempting restart"
                    )
                    await asyncio.sleep(0.2)
                except Exception as e:
                    logger.exception(f"Unhandled exception in socket {e}, {repr(e)}")
                    if self._is_closed:
                        return  # Don't do anything if we're already closed
                    raise e

        def async_socket_wrap():
            event_loop = asyncio.new_event_loop()
            self.loop_wrap = LoopWrapper(event_loop)
            asyncio.set_event_loop(event_loop)
            self._socket_task = event_loop.create_task(
                run_socket(),
            )
            event_loop.run_forever()

            async def close_websocket():
                if self.socket is not None:
                    await self.socket.close()
                if self._socket_task is not None:
                    await self._socket_task

            event_loop.run_until_complete(close_websocket())

        # Start listening thread
        self.thread = threading.Thread(
            target=async_socket_wrap, name=f"socket-thread-{self.socket_url}"
        )
        self.thread.start()

    async def _async_send_all(self):
        """
        Underlying send wrapper that calls on the current websocket to send
        """
        if self.outgoing_queue.empty():
            return
        # TODO(#651) pop all messages and batch, rather than just one
        packet = self.outgoing_queue.get()
        send_str = json.dumps(packet.to_sendable_dict())
        try:
            await self.socket.send(send_str)
        except websockets.exceptions.ConnectionClosedOK:
            pass
        except websockets.exceptions.ConnectionClosedError as e:
            if not isinstance(e.__cause__, asyncio.CancelledError):
                logger.exception(f"Caught error in _async_send {e}")

    def enqueue_send(self, packet: "Packet") -> bool:
        """
        Send the packet given to the intended recipient.
        Return True on success and False on failure.
        """
        if self.socket is None:
            return False
        if self.socket.closed:
            return False

        self.outgoing_queue.put(packet)

        loop_wrap = self.loop_wrap
        if loop_wrap is None:
            return False

        loop_wrap.execute_coro(self._async_send_all())
        return True
