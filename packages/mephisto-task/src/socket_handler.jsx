/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* eslint-disable react/no-direct-mutation-state */

import React from "react";
import { pythonTime } from "./utils";

/* ================= Data Model Constants ================= */

// System socket ids. Would be nice to pull these from a centralized location
const SERVER_SOCKET_ID = "mephisto_server";
const SYSTEM_SOCKET_ID = "mephisto";

// TODO figure out how to catch this state in the server and save it
// so that we can update the mephisto local state to acknowledge the occurrence
const STATUS_MEPHISTO_DISCONNECT = "mephisto disconnect";

// Socket function types
const PACKET_TYPE_HEARTBEAT = "heartbeat"; // Heartbeat from agent, carries current state
const PACKET_TYPE_ALIVE = "alive"; // packet from an agent alive event

const PACKET_TYPE_UPDATE_STATUS = "update_status"; // packet for updating agent client state
const PACKET_TYPE_CLIENT_BOUND_LIVE_UPDATE = "client_bound_live_update";
const PACKET_TYPE_MEPHISTO_BOUND_LIVE_UPDATE = "mephisto_bound_live_update";

const CONNECTION_STATUS = {
  FAILED: "failed",
  INITIALIZING: "initializing",
  WEBSOCKETS_FAILURE: "websockets_failure",
  CONNECTED: "connected",
  DISCONNECTED: "disconnected",
  RECONNECTING_ROUTER: "reconnecting_router",
  DISCONNECTED_ROUTER: "disconnected_router",
  RECONNECTING_SERVER: "reconnecting_server",
  DISCONNECTED_SERVER: "disconnected_server",
};

/* ================= Local Constants ================= */

const SEND_THREAD_REFRESH = 100;
const CONNECTION_DEAD_MEPHISTO_PING = 20 * 1000; // A minute of downtime is death
const REFRESH_SOCKET_MISSED_RESPONSES = 5;
const HEARTBEAT_TIME = 6 * 1000; // How often to send a heartbeat
const ROUTER_DEAD_TIMEOUT = 10; // Failed heartbeats before checking server

/* ============== Priority Queue Data Structure ============== */

// Initializing a 'priority queue'
class PriorityQueue {
  constructor() {
    this.data = [];
  }
  // Pushes an element as far back as it needs to go in order to insert
  push(element, priority) {
    priority = +priority;
    for (var i = 0; i < this.data.length && this.data[i][0] < priority; i++);
    this.data.splice(i, 0, [element, priority]);
  }
  // Remove and return the front element of the queue
  pop() {
    return this.data.shift();
  }
  // Show the front element of the queue
  peek() {
    return this.data[0];
  }
  // gets the size of the queue
  size() {
    return this.data.length;
  }
}

/* ================= Utility functions ================= */

let verbosity = 4;

// log the data when the verbosity is greater than the level
// (where low level is high importance)
// Levels: 0 - Error, unusual behavior, something worth notifying
//         1 - Server interactions on the message level, commands
//         2 - Server interactions on the heartbeat level
//         3 - Potentially important function calls
//         4 - Practically anything
function log(data, level) {
  if (verbosity >= level) {
    console.log(data);
  }
}

// Generate a random id
function uuidv4() {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
    var r = (Math.random() * 16) | 0,
      v = c == "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

function useValue(value, defaultValue) {
  if (value === null || value === undefined) {
    return defaultValue;
  } else {
    return value;
  }
}

/* ===================================================== */

function useMephistoSocket({
  onConnectionStatusChange,
  onLiveUpdate,
  onStatusUpdate /*, onStatusUpdate */,
  config = {},
}) {
  const initialState = {
    heartbeat_id: null, // Timeout id for heartbeat thread
    socket_terminated: false, // Flag for intentional socket closure
    setting_socket: false, // Flag for socket setup being underway
    heartbeats_without_response: 0, // HBs to the router without a pong back
    last_mephisto_ping: Date.now(),
    used_update_ids: [],
  };

  const [state, setState] = React.useReducer(
    (state, newState) => ({
      ...state,
      ...newState,
    }),
    initialState
  );

  const socket = React.useRef();
  const queue = React.useRef(new PriorityQueue());
  const callbacks = React.useRef();

  React.useEffect(() => {
    callbacks.current = {
      /* The sendingThread is a background interval timed thread that
       * accumulates queued packets and sends them through the socket,
       * retrying as needed */
      sendingThread: sendingThread,
      /* The heartbeatThread is a background interval timed thread that
       * pings the backend intermittently to ensure a persistent connection */
      heartbeatThread: heartbeatThread,
      /* Permanently closes the socket */
      closeSocket: closeSocket,
      /* Initializes the websocket and heartbeat thread. This is also called
       * when the socket connection is found to have issues and needs
       * to be retried */
      setupWebsocket: setupWebsocket,
      /* Queues up a packet to be sent over the websocket, retrying as needed
       * to ensure the packet gets sent. The sendingThread processes this queue */
      enqueuePacket: enqueuePacket,
      /* Sends a heartbeat to the backend. The heartbeat is not queued and is
       * sent to the socket directly */
      sendHeartbeat: sendHeartbeat,
    };
  });

  // The function exposed to the frontend client to start
  // the socket. Expects an agentId to be specified.
  function connect(agentId) {
    onConnectionStatusChange(CONNECTION_STATUS.INITIALIZING);
    callbacks.current.setupWebsocket();
    callbacks.current.sendingThread();
    const messageSenderThreadId = window.setInterval(
      () => callbacks.current.sendingThread(),
      useValue(config.sendThreadRefresh, SEND_THREAD_REFRESH)
    );
    setState({ agentId, messageSenderThreadId });
  }

  function sendingThread() {
    if (state.socket_terminated) {
      return;
    }

    // Can't act on an empty queue
    if (queue.current.size() > 0) {
      // Can't act if the send time for the next thing to send
      // is in the future
      if (Date.now() > queue.current.peek()[1]) {
        const item = queue.current.pop();
        const [event, queue_time] = item;

        const success = resilientPacketSend(event);
        if (!success) {
          queue.current.push(event, queue_time); // This message needs to be retried
        }
      }
    }
  }

  // Attempts to send a packet over the socket. If there are issues with
  // the socket, the socket will be restarted.
  // Returns: true if the packet was sent successfully
  //          false if there was an issue and a socket restart was initiated
  function resilientPacketSend(event) {
    if (socket.current.readyState == 0) {
      return false;
    } else if (socket.current.readyState > 1) {
      log("Socket not in ready state, restarting if possible", 2);
      attemptSocketRestart();
      return false;
    }
    try {
      socket.current.send(JSON.stringify(event.packet));
      if (event.callback !== undefined) {
        event.callback(event.packet);
      }
      return true;
    } catch (e) {
      attemptSocketRestart();
      return false;
    }
  }

  function attemptSocketRestart() {
    setTimeout(() => {
      try {
        socket.current.close();
      } catch (e) {
        log("Server had error " + e + " when closing after an error", 1);
      }
      callbacks.current.setupWebsocket();
    }, 0);
  }

  function enqueuePacket(eventType, data, callback) {
    var time = Date.now();
    if (data.update_id === undefined) {
      data.update_id = uuidv4();
    }

    var packet = {
      packet_type: eventType,
      subject_id: state.agentId,
      data: data,
      client_timestamp: pythonTime(),
    };

    var event = {
      packet: packet,
      callback: callback,
    };

    queue.current.push(event, time);
  }

  function sendLiveUpdate(message) {
    return new Promise((resolve) => {
      callbacks.current.enqueuePacket(
        PACKET_TYPE_MEPHISTO_BOUND_LIVE_UPDATE,
        message,
        (msg) => {
          resolve(msg.data);
        }
      );
    });
  }

  function setupWebsocket() {
    if (state.setting_socket || state.socket_terminated) {
      return;
    }

    // Note we are setting up the socket, ready to clear on failure
    setState({ setting_socket: true });

    // allow 4 seconds for the socket to be set up
    window.setTimeout(() => setState({ setting_socket: false }), 4000);

    let browserUrl = window.location;

    // Inherit socket protocol from web address protocol
    let socketProtocol = browserUrl.protocol == "https:" ? "wss://" : "ws://";
    let socketUrl =
      socketProtocol + browserUrl.hostname + ":" + browserUrl.port;
    socket.current = new WebSocket(socketUrl);

    // TODO if socket setup fails here, see if 404 or timeout, then check
    // other reasonable domain. If that succeeds, assume the server died.

    socket.current.onmessage = (event) => {
      parseSocketMessage(JSON.parse(event.data));
    };

    socket.current.onopen = () => {
      log("Server connected.", 2);

      /* sendAlive */
      callbacks.current.enqueuePacket(PACKET_TYPE_ALIVE, {}, () => {
        onConnectionStatusChange(CONNECTION_STATUS.CONNECTED);
      });

      window.setTimeout(() => {
        if (socket.current.readyState !== 1 && !state.socket_terminated) {
          onConnectionStatusChange(CONNECTION_STATUS.FAILED);
        }
      }, 10000);
      window.setTimeout(() => callbacks.current.sendHeartbeat(), 500);

      if (state.heartbeat_id == null) {
        const heartbeat_id = window.setInterval(
          () => callbacks.current.heartbeatThread(),
          useValue(config.heartbeatTime, HEARTBEAT_TIME)
        );
        setState({ heartbeat_id: heartbeat_id });
      }

      setState({
        setting_socket: false,
      });
    };

    socket.current.onerror = (event) => {
      console.error(event);
      attemptSocketRestart();
    };

    socket.current.onclose = () => {
      log("Server closing.", 3);
      onConnectionStatusChange(CONNECTION_STATUS.DISCONNECTED);
    };
  }

  function parseSocketMessage(packet) {
    if (packet.packet_type == PACKET_TYPE_CLIENT_BOUND_LIVE_UPDATE) {
      let used_update_ids = state.used_update_ids;

      if (used_update_ids.includes(packet.data.update_id)) {
        // Skip this message, it's a duplicate
        log("Skipping existing update_id " + packet.data.update_id, 3);
        return;
      } else {
        let new_update_ids = [...used_update_ids, packet.data.update_id];
        setState({ used_update_ids: new_update_ids });
      }
      onLiveUpdate(packet.data);
    } else if (packet.packet_type == PACKET_TYPE_UPDATE_STATUS) {
      onStatusUpdate(packet.data); // packet.data looks like - {status: "<>"}
    } else if (packet.packet_type == PACKET_TYPE_HEARTBEAT) {
      setState({
        last_mephisto_ping: packet.data["last_mephisto_ping"],
        heartbeats_without_response: 0,
      });
    }
  }

  // Thread sends heartbeats through the socket for as long we are connected
  function heartbeatThread() {
    // TODO fail properly and update state to closed when the host dies for
    // a long enough period. Once this says "disconnected" it should be
    // disconnected
    if (state.socket_terminated) {
      // No reason to keep a heartbeat if the socket is closed
      window.clearInterval(state.heartbeat_id);
      setState({ heartbeat_id: null });
      return;
    }

    // we're not getting responses from the server, perhaps the socket is stale
    if (
      state.heartbeats_without_response ===
      useValue(
        config.refreshSocketMissedResponses,
        REFRESH_SOCKET_MISSED_RESPONSES
      )
    ) {
      onConnectionStatusChange(CONNECTION_STATUS.RECONNECTING_ROUTER);
      attemptSocketRestart();
    }

    // we won't try any more, fails
    if (
      state.heartbeats_without_response >=
      useValue(config.routerDeadTimeout, ROUTER_DEAD_TIMEOUT)
    ) {
      onConnectionStatusChange(CONNECTION_STATUS.DISCONNECTED_ROUTER);
      callbacks.current.closeSocket();
    }

    // Check to see if we've disconnected from the server
    let time_since_last_ping = Date.now() - state.last_mephisto_ping;
    if (
      time_since_last_ping >
      useValue(config.connectionDeadMephistoPing, CONNECTION_DEAD_MEPHISTO_PING)
    ) {
      callbacks.current.closeSocket();
      onStatusUpdate({
        status: STATUS_MEPHISTO_DISCONNECT,
      });
      onConnectionStatusChange(CONNECTION_STATUS.DISCONNECTED_SERVER);
      window.clearInterval(state.heartbeat_id);
      setState({ heartbeat_id: null });
      return;
    }

    callbacks.current.sendHeartbeat();
  }

  function sendHeartbeat() {
    resilientPacketSend({
      packet: {
        packet_type: PACKET_TYPE_HEARTBEAT,
        subject_id: state.agentId,
        client_timestamp: pythonTime(),
      },
    });
    setState({
      heartbeats_without_response: state.heartbeats_without_response + 1,
    });
  }

  function closeSocket() {
    if (!state.socket_terminated) {
      log("Socket closing", 3);
      socket.current.close();
      setState({ socket_terminated: true });
    } else {
      log("Socket already closed", 2);
    }
  }

  return {
    connect: connect,
    destroy: () => callbacks.current.closeSocket(),
    sendLiveUpdate: sendLiveUpdate,
  };
}

export { useMephistoSocket, CONNECTION_STATUS };
