#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from abc import ABC, abstractmethod
from queue import Queue
import asyncio

from typing import Callable, Optional, TYPE_CHECKING
from mephisto.data_model.packet import Packet
from mephisto.operations.datatypes import LoopWrapper

STATUS_CHECK_TIME = 4

if TYPE_CHECKING:
    from mephisto.data_model.packet import Packet


class Channel(ABC):
    """
    Manages the API between the ClientIOHandler and the server
    that is produced by the architect.

    Should be able to be configured by an architect, and used to
    communicate with that server based on the queries that a
    ClientIOHandler needs to run a job
    """

    def __init__(
        self,
        channel_id: str,
        on_channel_open: Callable[[str], None],
        on_catastrophic_disconnect: Callable[[str], None],
        on_message: Callable[[str, Packet], None],
    ):
        """
        Create a channel by the given id, and initialize any resources that
        will later be required during the `open` call.

        Children classes will likely need to accept additional parameters

        on_channel_open should be called when the channel is first alive.
            It takes the channel id as the only argument.
        on_catastrophic_disconnect should only be called if the channel
            is entirely unable to connect to the server and any ongoing
            jobs should be killed.
            It takes the channel id as the only argument.
        on_message should be called whenever this channel receives a message
            from the server.
            It takes the channel id as the first argument and the received
            packet as the second argument.
        """
        self.channel_id = channel_id
        self.on_channel_open = on_channel_open
        self.on_catastrophic_disconnect = on_catastrophic_disconnect
        self.on_message = on_message
        self.loop_wrap: Optional[LoopWrapper] = None
        self.outgoing_queue: "Queue[Packet]" = Queue()

    @abstractmethod
    def is_closed(self):
        """
        Return whether or not this connection has been explicitly closed
        by the ClientIOHandler or another source.
        """

    @abstractmethod
    def close(self):
        """
        Close this channel, and ensure that all threads and surrounding
        resources are cleaned up
        """

    @abstractmethod
    def is_alive(self):
        """
        Return if this channel is actively able to send/recieve messages.
        Should be False until a connection has been established with the
        server.
        """

    @abstractmethod
    def open(self):
        """
        Do whatever is necessary to 'connect' this socket to the server
        """

    @abstractmethod
    def enqueue_send(self, packet: "Packet") -> bool:
        """
        Enqueue and send the packet given to the intended recipient.
        Return True on success and False on failure.
        """
