import React, { Children } from "react";
import { useMephistoTask, doesSupportWebsockets } from "./index";
import { useMephistoSocket, CONNECTION_STATUS } from "./socket_handler.jsx";

/* ================= Agent State Constants ================= */

const STATUS_NONE = "none";
const STATUS_ONBOARDING = "onboarding";
const STATUS_WAITING = "waiting";
const STATUS_IN_TASK = "in task";
const STATUS_DONE = "done";
const STATUS_DISCONNECT = "disconnect";
const STATUS_TIMEOUT = "timeout";
const STATUS_PARTNER_DISCONNECT = "partner disconnect";
const STATUS_EXPIRED = "expired";
const STATUS_RETURNED = "returned";
const STATUS_MEPHISTO_DISCONNECT = "mephisto disconnect";

const STATUS = {
  STATUS_NONE,
  STATUS_ONBOARDING,
  STATUS_WAITING,
  STATUS_IN_TASK,
  STATUS_DONE,
  STATUS_DISCONNECT,
  STATUS_TIMEOUT,
  STATUS_PARTNER_DISCONNECT,
  STATUS_EXPIRED,
  STATUS_RETURNED,
  STATUS_MEPHISTO_DISCONNECT,
};

const useMephistoLiveTask = function (props) {
  const [connectionStatus, setConnectionStatus] = React.useState("");
  const [agentState, setAgentState] = React.useState(null);
  const [agentStatus, setAgentStatus] = React.useState(null);

  const taskProps = useMephistoTask();
  const socketProps = useMephistoSocket({
    onStatusChange: (status) => {
      setConnectionStatus(status);
      //props.onStatusChange(status);
    },
    onStateUpdate: ({ state, status }) => {
      setAgentState(state);
      setAgentStatus(status);
      props.onStateUpdate({ state, status });
    },
    onMessageReceived: (message) => {
      props.onMessageReceived(message);
    },
  });

  if (!doesSupportWebsockets()) {
    taskProps.blockedReason = "no_websockets";
  }

  return {
    ...taskProps,
    ...socketProps,
    connectionStatus,
    agentState,
    agentStatus,
  };
};

export { useMephistoLiveTask, useMephistoSocket, STATUS, CONNECTION_STATUS };
