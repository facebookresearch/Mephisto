/* Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
"use strict";

const DEBUG = false;
const CURR_MEPHISTO_TASK_VERSION = "2.0.0";

// TODO add some testing to launch this server and communicate with it

const bodyParser = require("body-parser");
const express = require("express");
const http = require("http");
const fs = require("fs");
const WebSocket = require("ws");
const multer = require("multer");
const path = require("path");

const task_directory_name = "static";

const PORT = process.env.PORT || 3000;

// Generate a random id
function uuidv4() {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
    var r = (Math.random() * 16) | 0,
      v = c == "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

// Initialize app
const app = express();
app.use(bodyParser.text());
app.use(
  bodyParser.urlencoded({
    extended: true,
  })
);
app.use(bodyParser.json());

var storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, "/tmp/");
  },
  filename: function (req, file, cb) {
    const uniqueSuffix = Date.now() + "-" + Math.round(Math.random() * 1e9);
    cb(null, uniqueSuffix + "-" + file.fieldname + "-" + file.originalname);
  },
});

var upload = multer({ storage: storage });

const server = http.createServer(app);

// ======= <Sockets and Agents> ========

const FAILED_RECONNECT_TIME = 10000;
const FAILED_PING_TIME = 15000;

// TODO can we pull all these from somewhere, make sure they're testable
// and show they're the same as the python ones?
const STATUS_NONE = "none";
const STATUS_ACCEPTED = "accepted";
const STATUS_ONBOARDING = "onboarding";
const STATUS_WAITING = "waiting";
const STATUS_IN_TASK = "in task";
const STATUS_COMPLETED = "completed";
const STATUS_DISCONNECT = "disconnect";
const STATUS_TIMEOUT = "timeout";
const STATUS_PARTNER_DISCONNECT = "partner disconnect";
const STATUS_EXPIRED = "expired";
const STATUS_RETURNED = "returned";
const STATUS_APPROVED = "approved";
const STATUS_SOFT_REJECTED = "soft_rejected";
const STATUS_REJECTED = "rejected";

const SYSTEM_SOCKET_ID = "mephisto"; // TODO pull from somewhere

const PACKET_TYPE_ALIVE = "alive";
const PACKET_TYPE_SUBMIT_ONBOARDING = "submit_onboarding";
const PACKET_TYPE_SUBMIT_UNIT = "submit_unit";
const PACKET_TYPE_CLIENT_BOUND_LIVE_UPDATE = "client_bound_live_update";
const PACKET_TYPE_MEPHISTO_BOUND_LIVE_UPDATE = "mephisto_bound_live_update";
const PACKET_TYPE_REGISTER_AGENT = "register_agent";
const PACKET_TYPE_AGENT_DETAILS = "agent_details";
const PACKET_TYPE_UPDATE_STATUS = "update_status";
const PACKET_TYPE_REQUEST_STATUSES = "request_statuses";
const PACKET_TYPE_RETURN_STATUSES = "return_statuses";
const PACKET_TYPE_ERROR = "log_error";
const PACKET_TYPE_HEARTBEAT = "heartbeat";

// State for agents tracked by the server
class LocalAgentState {
  constructor(agent_id) {
    this.status = STATUS_NONE;
    this.agent_id = agent_id;
    this.unsent_messages = [];
    this.is_alive = false;
    this.last_ping = 0;
  }

  get_sendable_messages() {
    let sendable_messages = this.unsent_messages;
    this.unsent_messages = [];
    return sendable_messages;
  }
}

const wss = new WebSocket.Server({ server });

// Track connectionss
var agent_id_to_socket = {};
var socket_id_to_agent = {};
var mephisto_message_queue = [];
var main_thread_timeout = null;
var mephisto_socket = null;

// This is a mapping of connection id -> state
var agent_id_to_agent = {};

var pending_agent_requests = {};

var last_mephisto_ping = Date.now();

function debug_log() {
  if (DEBUG) {
    console.log.apply(null, arguments);
  }
}

function pythonTime() {
  return Date.now() / 1000;
}

// Handles sending a message through the socket
function _send_message(socket, packet) {
  if (!socket) {
    debug_log("No socket to send packet to", packet);
    // Socket doesn't exist - odd
    return;
  }

  if (socket.readyState == 3) {
    // Socket has already closed
    return;
  }

  packet["router_outgoing_timestamp"] = pythonTime();
  // Send the message through, with one retry a half second later
  socket.send(JSON.stringify(packet), function ack(error) {
    if (error === undefined) {
      return;
    }
    setTimeout(function () {
      socket.send(JSON.stringify(packet), function ack2(error2) {
        if (error2 === undefined) {
          return;
        } else {
          console.log(error2);
        }
      });
    }, 500);
  });
}

function find_or_create_agent(agent_id) {
  var agent = agent_id_to_agent[agent_id];
  if (agent === undefined) {
    debug_log("Am creating agent for " + agent_id);
    var agent = new LocalAgentState(agent_id);
    agent_id_to_agent[agent_id] = agent;
  }
  return agent;
}

function clear_agent(agent_id) {
  debug_log("Clearing agent " + agent_id);
  delete agent_id_to_agent[agent_id];
  let socket = agent_id_to_socket[agent_id];
  delete agent_id_to_socket[agent_id];
  if (socket !== undefined) {
    delete socket_id_to_agent[socket.id];
  }
}

// Open connections send alives to identify who they are,
// register them correctly here
function handle_alive(socket, alive_packet) {
  if (alive_packet.subject_id == SYSTEM_SOCKET_ID) {
    mephisto_socket = socket;
    console.log("System socket attached:");
    console.log(socket._socket.remoteAddress);
    if (main_thread_timeout === null) {
      debug_log("launching main thread");
      main_thread_timeout = setTimeout(main_thread, 50);
    }
  } else {
    var agent_id = alive_packet.subject_id;
    var agent = find_or_create_agent(agent_id);
    debug_log("Am linking socket for " + agent_id);
    agent.is_alive = true;
    agent_id_to_socket[agent_id] = socket;
    socket_id_to_agent[socket.id] = agent;
    send_status_for_agent(agent_id);
  }
}

function ensure_live_connection(agent) {
  let curr_status = agent.status;
  let last_ping = agent.last_ping;
  if (last_ping == 0) {
    return; // Not a live task, nothing to check
  }
  if (
    ![STATUS_ONBOARDING, STATUS_WAITING, STATUS_IN_TASK].includes(curr_status)
  ) {
    return; // Not in a live state, nothing to ensure
  }
  if (Date.now() - last_ping > FAILED_PING_TIME) {
    agent.status = STATUS_DISCONNECT;
    send_status_for_agent(agent.agent_id);
  }
}

// Return the status of all agents mapped by their agent id
function handle_get_agent_status(status_packet) {
  last_mephisto_ping = Date.now();
  let agent_statuses = {};
  for (let agent_id in agent_id_to_agent) {
    let agent = agent_id_to_agent[agent_id];
    ensure_live_connection(agent);
    agent_statuses[agent_id] = agent.status;
  }
  let packet = {
    packet_type: PACKET_TYPE_RETURN_STATUSES,
    subject_id: SYSTEM_SOCKET_ID,
    data: agent_statuses,
    client_timestamp: status_packet.server_timestamp,
    router_incoming_timestamp: status_packet.router_incoming_timestamp,
  };
  mephisto_message_queue.push(packet);
}

function handle_update_local_status(status_packet) {
  let agent_id = status_packet.subject_id;
  let agent = find_or_create_agent(agent_id);
  if (status_packet.data.status != undefined) {
    agent.status = status_packet.data.status;
  }
}

// Handle a message being sent to a frontend agent
function forward_to_agent(packet) {
  let agent = find_or_create_agent(packet.subject_id);
  let socket = agent_id_to_socket[agent.agent_id];
  if (socket) {
    _send_message(socket, packet);
  } else {
    debug_log("Socket not open yet, adding message to agent queue", packet);
    agent.unsent_messages.push(packet);
  }
}

function _followup_possible_disconnect(agent) {
  if (!agent.is_alive) {
    agent.status = STATUS_DISCONNECT;
    debug_log("Agent disconnected", agent);
  }
}

function handle_possible_disconnect(agent) {
  debug_log("Possible disconnect", agent);
  agent.is_alive = false;

  // Give the agent some time to possibly reconnect
  setTimeout(() => _followup_possible_disconnect(agent), FAILED_RECONNECT_TIME);
}

function send_status_for_agent(agent_id) {
  let agent = find_or_create_agent(agent_id);
  let packet = {
    packet_type: PACKET_TYPE_UPDATE_STATUS,
    subject_id: agent_id,
    data: {
      status: agent.status,
    },
  };
  forward_to_agent(packet);
}

// Register handlers
wss.on("connection", function (socket) {
  socket.id = uuidv4();
  console.log("Client connected");
  // Disconnects are logged
  socket.on("disconnect", function () {
    console.log("socket disconnected");
    var agent = socket_id_to_agent[socket.id];
    if (agent !== undefined) {
      handle_possible_disconnect(agent);
    }
  });

  socket.on("error", (err) => {
    console.log("Caught socket error, probably closed!");
    console.log(err);
    var agent = socket_id_to_agent[socket.id];
    if (agent !== undefined) {
      handle_possible_disconnect(agent);
    }
  });

  // handles routing a packet to the desired recipient
  socket.on("message", function (packet) {
    try {
      packet = JSON.parse(packet);
      packet["router_incoming_timestamp"] = pythonTime();
      if (packet["packet_type"] == PACKET_TYPE_REQUEST_STATUSES) {
        debug_log("Mephisto requesting status");
        handle_get_agent_status(packet);
      } else if (
        packet["packet_type"] == PACKET_TYPE_MEPHISTO_BOUND_LIVE_UPDATE
      ) {
        debug_log("Mephisto-bound action: ", packet);
        mephisto_message_queue.push(packet);
      } else if (
        packet["packet_type"] == PACKET_TYPE_CLIENT_BOUND_LIVE_UPDATE
      ) {
        debug_log("Client-bound action: ", packet);
        forward_to_agent(packet);
      } else if (packet["packet_type"] == PACKET_TYPE_ERROR) {
        mephisto_message_queue.push(packet);
      } else if (packet["packet_type"] == PACKET_TYPE_ALIVE) {
        debug_log("Agent alive: ", packet);
        handle_alive(socket, packet);
      } else if (packet["packet_type"] == PACKET_TYPE_UPDATE_STATUS) {
        debug_log("Update agent status", packet);
        handle_update_local_status(packet);
        forward_to_agent(packet);
      } else if (packet["packet_type"] == PACKET_TYPE_AGENT_DETAILS) {
        let request_id = packet["data"]["request_id"];
        if (request_id === undefined) {
          request_id = packet["subject_id"];
        }
        let res_obj = pending_agent_requests[request_id];
        if (res_obj) {
          res_obj.json(packet);
          delete pending_agent_requests[request_id];
        }
      } else if (packet["packet_type"] == PACKET_TYPE_HEARTBEAT) {
        packet["data"] = { last_mephisto_ping: last_mephisto_ping };
        let agent_id = packet["subject_id"];
        let agent = agent_id_to_agent[agent_id];
        if (agent !== undefined) {
          agent.is_alive = true;
          agent.last_ping = Date.now();
          packet.data.status = agent.status;
          if (
            agent_id_to_socket[agent.agent_id] != socket &&
            agent_id_to_socket[agent.agent_id] != undefined
          ) {
            // Not communicating to the _correct_ socket, update
            debug_log("Updating socket for ", agent);
            agent_id_to_socket[agent.agent_id] = socket;
            socket_id_to_agent[socket.id] = agent;
          }
        }
        forward_to_agent(packet);
      }
    } catch (error) {
      console.log("Transient error on message");
      console.log(error);
    }
  });
});

server.listen(PORT, function () {
  console.log("Listening on %d", server.address().port);
});

// ============ </Sockets and Agents> ==============

// ======================= <Threads> =======================

// TODO add crash checking around this thread?
function main_thread() {
  try {
    // Handle active connections message sends
    for (const agent_id in agent_id_to_socket) {
      let agent_state = agent_id_to_agent[agent_id];
      if (!agent_state.is_alive) {
        continue;
      }
      let sendable_messages = agent_state.get_sendable_messages();
      if (sendable_messages.length > 0) {
        let socket = agent_id_to_socket[agent_id];
        // TODO send all these messages in a batch
        for (const packet of sendable_messages) {
          _send_message(socket, packet);
        }
      }
    }

    // Handle sending batches to the mephisto python client
    let mephisto_messages = [];
    while (mephisto_message_queue.length > 0) {
      mephisto_messages.push(mephisto_message_queue.shift());
    }
    if (mephisto_messages.length > 0) {
      for (const packet of mephisto_messages) {
        _send_message(mephisto_socket, packet);
      }
    }
  } catch (error) {
    console.log("Transient error in main thread?");
    console.log(error);
  }

  // Re-call this thead, as it should run forever
  main_thread_timeout = setTimeout(main_thread, 50);
}

// ======================= </Threads> ======================

// ===================== <Routing> ========================
app.post("/request_agent", function (req, res) {
  var provider_data = req.body.provider_data;
  var client_timestamp = req.body.client_timestamp;
  var request_id = uuidv4();

  let request_packet = {
    packet_type: PACKET_TYPE_REGISTER_AGENT,
    subject_id: request_id,
    data: {
      provider_data: provider_data,
      request_id: request_id,
    },
    client_timestamp: client_timestamp,
    router_incoming_timestamp: pythonTime(),
  };

  pending_agent_requests[request_id] = res;
  _send_message(mephisto_socket, request_packet);
  // TODO set a timeout to expire this request rather than leave the worker hanging
});

app.post("/submit_onboarding", function (req, res) {
  var provider_data = req.body.provider_data;
  var client_timestamp = req.body.client_timestamp;
  var request_id = uuidv4();

  let agent_id = provider_data.USED_AGENT_ID;
  debug_log("Am submitting onboarding for " + agent_id);
  delete provider_data.USED_AGENT_ID;

  provider_data.onboarding_data = provider_data.onboarding_data || {};

  provider_data.request_id = request_id;

  let submit_packet = {
    packet_type: PACKET_TYPE_SUBMIT_ONBOARDING,
    subject_id: agent_id,
    data: provider_data,
    client_timestamp: client_timestamp,
    router_incoming_timestamp: pythonTime(),
  };

  pending_agent_requests[request_id] = res;
  _send_message(mephisto_socket, submit_packet);
  clear_agent(agent_id);
});

app.post("/submit_task", upload.any(), function (req, res) {
  const {
    USED_AGENT_ID: agent_id,
    final_data: final_data,
    final_string_data: final_string_data,
    client_timestamp: client_timestamp,
  } = req.body;
  let extracted_data = final_data;
  if (final_string_data) {
    extracted_data = JSON.parse(final_string_data);
  }
  if (req.files) {
    extracted_data.files = req.files;
  }
  let submit_packet = {
    packet_type: PACKET_TYPE_SUBMIT_UNIT,
    subject_id: agent_id,
    data: extracted_data,
    client_timestamp: client_timestamp,
    router_incoming_timestamp: pythonTime(),
  };
  _send_message(mephisto_socket, submit_packet);
  res.json({ status: "Submitted!" });

  // Cleanup local state for a task that's already submitted
  if (agent_id in agent_id_to_agent) {
    delete agent_id_to_agent[agent_id];
  }
  if (agent_id in agent_id_to_socket) {
    let socket_id = agent_id_to_socket[agent_id].id;
    delete agent_id_to_socket[agent_id];
    delete socket_id_to_agent[socket_id];
  }
});

app.post("/log_error", function (req, res) {
  const {
    USED_AGENT_ID: agent_id,
    error_data: error_data,
    client_timestamp: client_timestamp,
  } = req.body;
  let log_packet = {
    packet_type: PACKET_TYPE_ERROR,
    subject_id: agent_id,
    data: error_data,
    client_timestamp: client_timestamp,
    router_incoming_timestamp: pythonTime(),
  };
  _send_message(mephisto_socket, log_packet);
  res.json({ status: "Error log sent!" });
});

app.get("/task_config.json", function (req, res) {
  const { mephisto_task_version } = req.query;
  if (mephisto_task_version !== CURR_MEPHISTO_TASK_VERSION) {
    mephisto_message_queue.push({
      packet_type: PACKET_TYPE_ERROR,
      subject_id: SYSTEM_SOCKET_ID,
      data: {
        error_type: "version-mismatch",
        text:
          "Package `mephisto-task` version mismatch. Expected " +
          "version " +
          CURR_MEPHISTO_TASK_VERSION +
          " but frontend is currently using " +
          mephisto_task_version +
          ". This may cause unexpected errors, be sure to " +
          "update your `mephisto-task` dependency with `npm " +
          "install mephisto-task@" +
          CURR_MEPHISTO_TASK_VERSION +
          " --save`. If this warning still persists or the " +
          "version isn't found, please open an issue at " +
          "https://github.com/facebookresearch/Mephisto/issues",
      },
    });
  }
  res.sendFile(__dirname + "/static/task_config.json");
});

// Quick status check for this server
app.get("/is_alive", function (req, res) {
  res.json({ status: "Alive!" });
});

// Returns server time for now
app.get("/get_timestamp", function (req, res) {
  res.json({ timestamp: Date.now() }); // in milliseconds
});

app.get("/task_index", function (req, res) {
  // TODO how do we pass the task config to the frontend?
  res.render("index.html");
});

app.get("/download_file/:file", function (req, res) {
  var ip =
    req.ip ||
    req.headers["x-forwarded-for"] ||
    req.connection.remoteAddress ||
    req.socket.remoteAddress ||
    req.connection.socket.remoteAddress;
  if (ip == mephisto_socket._socket.remoteAddress) {
    res.sendFile(path.join("/tmp/", req.params.file), function (err) {
      if (err) {
        console.log(err);
        res.status(err.status).end();
      }
    });
  } else {
    res.sendFile(path.join("/tmp/", req.params.file), function (err) {
      if (err) {
        console.log(err);
        res.status(err.status).end();
      }
    });
    // TODO only return the files for requests from the origin
    // res.status(403).end();
  }
});

app.use(express.static("static"));

// ======================= </Routing> =======================
