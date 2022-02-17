/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

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

const STATUS_TO_TEXT_MAP = {
  [AGENT_STATUS.EXPIRED]:
    "This task is no longer available to be completed. " +
    " Please return it and try a different task",
  [AGENT_STATUS.TIMEOUT]:
    "You took to long to respond to this task, and have timed out. " +
    "The task is no longer available, please return it.",
  [AGENT_STATUS.DISCONNECT]:
    "You have disconnected from our server during the duration of the task. " +
    "If you have done substantial work, please reach out to see if we can recover it. ",
  [AGENT_STATUS.RETURNED]:
    "You have disconnected from our server during the duration of the task. " +
    "If you have done substantial work, please reach out to see if we can recover it. ",
  [AGENT_STATUS.PARTNER_DISCONNECT]:
    "One of your partners has disconnected while working on this task. We won't penalize " +
    "you for them leaving, so please submit this task as is.",
  [AGENT_STATUS.MEPHISTO_DISCONNECT]:
    "Our server appears to have gone down during the " +
    "duration of this Task. Please send us a message if you've done " +
    "substantial work and we can find out if the task is complete enough to " +
    "compensate.",
};

const useMephistoLiveTask = function (props) {
  const [connectionStatus, setConnectionStatus] = React.useState("");
  const [agentStatus, setAgentStatus] = React.useState(null);

  const defaultConnectionHook = useMephistoSocket;
  const useConnectionHook = props.customConnectionHook || defaultConnectionHook;

  const taskProps = useMephistoTask();

  const { initialTaskData } = taskProps;

  function handleLiveUpdate(liveUpdate) {
    props.onLiveUpdate && props.onLiveUpdate(liveUpdate);
  }

  React.useEffect(() => {
    if (initialTaskData?.past_live_updates) {
      for (const liveUpdate of initialTaskData.past_live_updates) {
        handleLiveUpdate(liveUpdate);
      }
    }
  }, [initialTaskData]);

  const socketProps = useConnectionHook({
    onConnectionStatusChange: (connectionStatus) => {
      setConnectionStatus(connectionStatus);
    },
    onStatusUpdate: ({ status }) => {
      setAgentStatus(status);
      props.onStatusUpdate && props.onStatusUpdate({ status });
    },
    onLiveUpdate: handleLiveUpdate,
  });

  if (!doesSupportWebsockets()) {
    taskProps.blockedReason = "no_websockets";
  }

  return {
    ...taskProps,
    ...socketProps,
    connectionStatus,
    agentStatus,
  };
};

export {
  useMephistoLiveTask,
  useMephistoSocket,
  AGENT_STATUS,
  STATUS_TO_TEXT_MAP,
  CONNECTION_STATUS,
};
