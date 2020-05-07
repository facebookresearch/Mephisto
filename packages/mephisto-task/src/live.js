import React from "react";
import { useMephistoTask, doesSupportWebsockets } from "./index";
import { useMephistoSocket, CONNECTION_STATUS } from "./socket_handler.jsx";

/* ================= Agent State Constants ================= */

const AGENT_STATUS = {
  NONE: "none",
  ONBOARDING: "onboarding",
  WAITING: "waiting",
  IN_TASK: "in task",
  DONE: "done",
  DISCONNECT: "disconnect",
  TIMEOUT: "timeout",
  PARTNER_DISCONNECT: "partner disconnect",
  EXPIRED: "expired",
  RETURNED: "returned",
  MEPHISTO_DISCONNECT: "mephisto disconnect",
};

const useMephistoLiveTask = function (props) {
  const [connectionStatus, setConnectionStatus] = React.useState("");
  const [agentState, setAgentState] = React.useState(null);
  const [agentStatus, setAgentStatus] = React.useState(null);

  const taskProps = useMephistoTask();
  const socketProps = useMephistoSocket({
    onConnectionStatusChange: (connectionStatus) => {
      setConnectionStatus(connectionStatus);
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

export {
  useMephistoLiveTask,
  useMephistoSocket,
  AGENT_STATUS,
  CONNECTION_STATUS,
};
