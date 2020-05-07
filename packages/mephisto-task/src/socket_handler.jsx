/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

/* eslint-disable react/no-direct-mutation-state */

import React from "react";

/* ================= Data Model Constants ================= */

// System socket ids. Would be nice  to pull these from a centralized location
const SERVER_SOCKET_ID = "mephisto_server";
const SYSTEM_SOCKET_ID = "mephisto";

// TODO figure out how to catch this state in the server and save it
// so that we can update the mephisto local state to acknowledge the occurrence
const STATUS_MEPHISTO_DISCONNECT = "mephisto disconnect";

// Socket function types
const PACKET_TYPE_HEARTBEAT = "heartbeat"; // Heartbeat from agent, carries current state
const PACKET_TYPE_AGENT_ALIVE = "alive"; // packet from an agent alive event

const PACKET_TYPE_UPDATE_STATE = "update_status"; // packet for updating agent client state
const PACKET_TYPE_AGENT_ACTION = "agent_action";

/* ================= Local Constants ================= */

const SEND_THREAD_REFRESH = 100;
const CONNECTION_DEAD_MEPHISTO_PING = 20 * 1000; // A minute of downtime is death
const REFRESH_SOCKET_MISSED_RESPONSES = 5;
const HEARTBEAT_TIME = 6000; // One heartbeat every so often
const ROUTER_DEAD_TIMEOUT = 10; // Failed heartbeats before checking server
// TODO rework server connectivity functionality.

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

class SocketHandler extends React.Component {
  constructor(props) {
    super(props);
    this.q = new PriorityQueue();
    this.socket = null;
    this.state = {
      heartbeat_id: null, // Timeout id for heartbeat thread
      socket_closed: false, // Flag for intentional socket closure
      setting_socket: false, // Flag for socket setup being underway
      heartbeats_without_response: 0, // HBs to the router without a pong back
      last_mephisto_ping: Date.now(),
    };
  }

  /*************************************************
   * ----- Packet sending/management functions ------
   *
   * The following functions comprise the outgoing
   * packet management system. Messages are enqueued
   * using sendPacket. The sendingThread works through
   * the queued packets and passes them through sendHelper
   * when appropriate and then pushes the packet through
   * the socket using safePacketSend.
   **/

  // Push a packet through the socket, call the callback on that packet data
  // if successful. Returns true on success and false on failure.
  safePacketSend(event) {
    if (this.socket.readyState == 0) {
      return false;
    } else if (this.socket.readyState > 1) {
      attemptSocketRestart();
      return false;
    }
    try {
      this.socket.send(JSON.stringify(event.packet));
      if (event.callback !== undefined) {
        event.callback(event.packet);
      }
      return true;
    } catch (e) {
      attemptSocketRestart();
      return false;
    }
  }

  attemptSocketRestart() {
    log("Socket not in ready state, restarting if possible", 2);
    try {
      this.socket.close();
    } catch (e) {
      log("Server had error " + e + " when closing after an error", 1);
    }
    this.setupSocket();
  }

  // Wrapper around packet sends that handles managing state
  // updates, as well as not sending packets that have already been sent
  trySend(event, queue_time) {
    var success = this.safePacketSend(event);

    if (!success) {
      this.q.push(packet, queue_time); // This message needs to be retried
    }
  }

  // Thread checks the message queue and handles pushing out new messages
  // as they are added to the queue
  sendingThread() {
    if (this.state.socket_closed) {
      return;
    }

    // Can't act on an empty queue
    if (this.q.size() > 0) {
      // Can't act if the send time for the next thing to send
      // is in the future
      if (Date.now() > this.q.peek()[1]) {
        var item = this.q.pop();
        var event = item[0];
        var t = item[1];
        this.trySend(event, t);
      }
    }
  }

  // Enqueues a message for sending, registers the message and callback
  enqueuePacket(event_type, data, callback) {
    var time = Date.now();
    let msg_id = uuidv4();

    var packet = {
      packet_type: event_type,
      sender_id: this.props.agent_id,
      receiver_id: SYSTEM_SOCKET_ID,
      data: data,
      msg_id: msg_id,
    };

    var event = {
      packet: packet,
      callback: callback,
    };

    this.q.push(event, time);
  }

  // Required function - The BaseApp class will call this function to enqueue
  // packet sends that are requested by the frontend user (worker)
  // TODO: shorten function argument signature to just task_data
  handleQueueMessage(text, task_data, callback) {
    let new_message_id = uuidv4();
    this.enqueuePacket(
      PACKET_TYPE_AGENT_ACTION,
      {
        text: text,
        task_data: task_data /* required */,
        id: this.props.agent_id /* required */,
        message_id: new_message_id /* required */,
        episode_done: false,
        /* TODO: ^perhaps extract out of this library into client code */
      },
      (msg) => {
        if (callback !== undefined) {
          callback();
        }
      }
    );
  }

  // way to send alive packets when expected to
  // an alive conveys an intent that the client that is connecting for the
  // first time, so initialization and registration can occur
  sendAlive() {
    this.enqueuePacket(PACKET_TYPE_AGENT_ALIVE, {}, () => {
      this.props.onStatusChange("connected");
    });
  }

  /**************************************************
   * ----- Packet reception infra and functions ------
   *
   * The following functions are all related to
   * handling incoming messages. It calls relevant callbacks
   * from the mephistoLiveTask
   **/

  parseSocketMessage(packet) {
    console.log(packet);
    if (packet.packet_type == PACKET_TYPE_AGENT_ACTION) {
      this.props.onNewData(packet.data);
    } else if (packet.packet_type == PACKET_TYPE_UPDATE_STATE) {
      this.props.onStateUpdate(packet.data); // Update packet {state: {}, status: "<>"}
      // TODO: Document that is_final is what closes the socket
      if (packet.data.state.is_final) {
        this.closeSocket();
      }
    } else if (packet.packet_type == PACKET_TYPE_HEARTBEAT) {
      this.setState({
        last_mephisto_ping: packet.data["last_mephisto_ping"],
        heartbeats_without_response: 0,
      });
    }
  }

  /**************************************************
   * ---------- socket lifecycle functions -----------
   *
   * These functions comprise the socket's ability to
   * start up, check it's health, restart, and close.
   * setupSocket registers the socket handlers, and
   * when the socket opens it sets a timeout for
   * having the Mephisto host ack the alive (failInitialize).
   * It also starts heartbeats (using heartbeatThread) if
   * they aren't already underway. On an error the socket
   * restarts. The heartbeat thread manages sending
   * heartbeats and tracking when the router responds
   * but the Mephisto host does not.
   **/

  // Sets up and registers the socket and the callbacks
  setupSocket() {
    if (this.state.setting_socket || this.state.socket_closed) {
      return;
    }

    // Note we are setting up the socket, ready to clear on failure
    this.setState({ setting_socket: true });

    // allow 4 seconds for the socket to be set up
    window.setTimeout(() => this.setState({ setting_socket: false }), 4000);

    let url = window.location;
    if (url.hostname == "localhost") {
      // Localhost can't always handle secure websockets, so we special case
      this.socket = new WebSocket("ws://" + url.hostname + ":" + url.port);
    } else {
      this.socket = new WebSocket("wss://" + url.hostname + ":" + url.port);
    }
    // TODO if socket setup fails here, see if 404 or timeout, then check
    // other reasonable domain. If that succeeds, assume the server died.

    this.socket.onmessage = (event) => {
      this.parseSocketMessage(JSON.parse(event.data));
    };

    this.socket.onopen = () => {
      log("Server connected.", 2);
      this.sendAlive();
      window.setTimeout(() => this.failInitialize(), 10000);
      window.setTimeout(() => this.sendHeartbeat(), 500);
      let heartbeat_id = null;
      if (this.state.heartbeat_id == null) {
        heartbeat_id = window.setInterval(
          () => this.heartbeatThread(),
          HEARTBEAT_TIME
        );
      } else {
        heartbeat_id = this.state.heartbeat_id;
      }
      this.setState({
        heartbeat_id: heartbeat_id,
        setting_socket: false,
      });
    };

    this.socket.onerror = () => {
      this.attemptSocketRestart();
    };

    this.socket.onclose = () => {
      log("Server closing.", 3);
      this.props.onStatusChange("disconnected");
    };
  }

  failInitialize() {
    // only cause a fail state change if the socket isn't already initialized
    if (this.socket.readyState !== 1) {
      this.props.onStatusChange("failed");
    }
  }

  closeSocket() {
    if (!this.state.socket_closed) {
      log("Socket closing", 3);
      this.socket.close();
      // TODO: consider renaming socket_closed to indicate a terminal close
      this.setState({ socket_closed: true });
    } else {
      log("Socket already closed", 2);
    }
  }

  componentDidMount() {
    console.log("mounting....");
    this.setupSocket();
    window.setInterval(() => this.sendingThread(), SEND_THREAD_REFRESH);
  }

  componentWillUnmount() {
    console.log("unmounting...");
  }

  sendHeartbeat() {
    this.safePacketSend({
      packet: {
        packet_type: PACKET_TYPE_HEARTBEAT,
        msg_id: uuidv4(),
        receiver_id: SERVER_SOCKET_ID,
        sender_id: this.props.agent_id,
        data: { agent_status: this.props.agent_status },
      },
    });
    this.setState({
      heartbeats_without_response: this.state.heartbeats_without_response + 1,
    });
  }

  // Thread sends heartbeats through the socket for as long we are connected
  heartbeatThread() {
    // TODO fail properly and update state to closed when the host dies for
    // a long enough period. Once this says "disconnected" it should be
    // disconnected
    if (this.state.socket_closed) {
      // No reason to keep a heartbeat if the socket is closed
      window.clearInterval(this.state.heartbeat_id);
      this.setState({ heartbeat_id: null });
      return;
    }

    // we're not getting responses from the server, perhaps the socket is stale
    if (
      this.state.heartbeats_without_response == REFRESH_SOCKET_MISSED_RESPONSES
    ) {
      this.props.onStatusChange("reconnecting_router");
      this.attemptSocketRestart();
    }

    // we won't try any more, fails
    if (this.state.heartbeats_without_response >= ROUTER_DEAD_TIMEOUT) {
      this.props.onStatusChange("disconnected_router");
      this.closeSocket();
    }

    // Check to see if we've disconnected from the server
    let time_since_last_ping = Date.now() - this.state.last_mephisto_ping;
    if (time_since_last_ping > CONNECTION_DEAD_MEPHISTO_PING) {
      this.closeSocket();
      let done_text =
        "Our server appears to have gone down during the \
        duration of this Task. Please send us a message if you've done \
        substantial work and we can find out if the task is complete enough to \
        compensate.";
      this.props.onStateUpdate({
        state: {
          done_text: done_text,
          task_done: true,
        },
        status: STATUS_MEPHISTO_DISCONNECT,
      });
      this.props.onStatusChange("disconnected_server");
      window.clearInterval(this.state.heartbeat_id);
      this.setState({ heartbeat_id: null });
    }

    this.sendHeartbeat();
  }

  // No rendering component for the SocketHandler
  render() {
    return this.props.children(this.handleQueueMessage) || null;
  }
}

export default SocketHandler;

/*
 ********************************************************************************
 ********************************************************************************
 ********************************************************************************
 ********************************************************************************s
 */

function useMephistoSocket({
  onStatusChange,
  onMessageReceived,
  onStateUpdate /*, onStateUpdate */,
}) {
  const initialState = {
    heartbeat_id: null, // Timeout id for heartbeat thread
    socket_terminated: false, // Flag for intentional socket closure
    setting_socket: false, // Flag for socket setup being underway
    heartbeats_without_response: 0, // HBs to the router without a pong back
    last_mephisto_ping: Date.now(),
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
      sendingThread: sendingThread,
      heartbeatThread: heartbeatThread,
      closeSocket: closeSocket,
      setupWebsocket: setupWebsocket,
      enqueuePacket: enqueuePacket,
      sendHeartbeat: sendHeartbeat,
    };
  });

  function connect(agentId) {
    callbacks.current.setupWebsocket();
    console.log("Connecting");
    callbacks.current.sendingThread();
    const messageSenderThreadId = window.setInterval(
      () => callbacks.current.sendingThread(),
      SEND_THREAD_REFRESH
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

        console.log("sending");
        console.log(event);

        const success = resilientPacketSend(event);
        if (!success) {
          queue.current.push(event, queue_time); // This message needs to be retried
        }
      }
    }
  }

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
    let messageId = uuidv4();

    var packet = {
      packet_type: eventType,
      sender_id: state.agentId,
      receiver_id: SYSTEM_SOCKET_ID,
      data: data,
      msg_id: messageId,
    };

    var event = {
      packet: packet,
      callback: callback,
    };

    queue.current.push(event, time);
  }

  function sendMessage(text, task_data) {
    let new_message_id = uuidv4();
    return new Promise((resolve) => {
      callbacks.current.enqueuePacket(
        PACKET_TYPE_AGENT_ACTION,
        {
          text: text,
          task_data: task_data /* required */,
          id: state.agentId /* required */,
          message_id: new_message_id /* required */,
          episode_done: false,
          /* TODO: ^perhaps extract out of this library into client code */
        },
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

    // Localhost can't always handle secure websockets, so we special case
    let socketProtocol =
      browserUrl.hostname == "localhost" ? "ws://" : "wss://";
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
      callbacks.current.enqueuePacket(PACKET_TYPE_AGENT_ALIVE, {}, () => {
        onStatusChange("connected");
      });

      window.setTimeout(() => {
        if (socket.current.readyState !== 1) {
          onStatusChange("failed");
        }
      }, 10000);
      window.setTimeout(() => callbacks.current.sendHeartbeat(), 500);

      if (state.heartbeat_id == null) {
        const heartbeat_id = window.setInterval(
          () => callbacks.current.heartbeatThread(),
          HEARTBEAT_TIME
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
      onStatusChange("disconnected");
    };
  }

  function parseSocketMessage(packet) {
    if (packet.packet_type == PACKET_TYPE_AGENT_ACTION) {
      onMessageReceived(packet.data);
    } else if (packet.packet_type == PACKET_TYPE_UPDATE_STATE) {
      console.log(packet);
      onStateUpdate(packet.data); // Update packet {state: {}, status: "<>"}
      // TODO: Document that is_final is what closes the socket
      if (packet.data.state.is_final) {
        callbacks.current.closeSocket();
      }
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
    if (state.heartbeats_without_response == REFRESH_SOCKET_MISSED_RESPONSES) {
      onStatusChange("reconnecting_router");
      attemptSocketRestart();
    }

    // we won't try any more, fails
    if (state.heartbeats_without_response >= ROUTER_DEAD_TIMEOUT) {
      onStatusChange("disconnected_router");
      callbacks.current.closeSocket();
    }

    // Check to see if we've disconnected from the server
    let time_since_last_ping = Date.now() - state.last_mephisto_ping;
    if (time_since_last_ping > CONNECTION_DEAD_MEPHISTO_PING) {
      callbacks.current.closeSocket();
      let done_text =
        "Our server appears to have gone down during the \
        duration of this Task. Please send us a message if you've done \
        substantial work and we can find out if the task is complete enough to \
        compensate.";
      onStateUpdate({
        state: {
          done_text: done_text,
          task_done: true,
        },
        status: STATUS_MEPHISTO_DISCONNECT,
      });
      onStatusChange("disconnected_server");
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
        msg_id: uuidv4(),
        receiver_id: SERVER_SOCKET_ID,
        sender_id: state.agentId,
        // data: { agent_status: this.props.agent_status },
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
      // TODO: consider renaming socket_closed to indicate a terminal close
      setState({ socket_terminated: true });
    } else {
      log("Socket already closed", 2);
    }
  }

  return {
    state: state,
    connect: connect,
    destroy: () => callbacks.current.closeSocket(),
    sendMessage: sendMessage,
  };
}

export { useMephistoSocket };
