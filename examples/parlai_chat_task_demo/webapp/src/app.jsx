/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";
import ReactDOM from "react-dom";
import { BaseFrontend } from "./components/core_components.jsx";

import { useMephistoLiveTask, AGENT_STATUS } from "mephisto-task";

/* ================= Application Components ================= */

const MephistoContext = React.createContext(null);
const CHAT_MODE = {
  WAITING: "waiting",
  INACTIVE: "inactive",
  DONE: "done",
  READY_FOR_INPUT: "ready_for_input",
  IDLE: "idle",
};

export { MephistoContext, CHAT_MODE };

function MainApp() {
  const [taskContext, updateContext] = React.useReducer(
    (oldContext, newContext) => Object.assign(oldContext, newContext),
    {}
  );

  const [messages, addMessage] = React.useReducer(
    (previousMessages, newMessage) => {
      // we clear messages by sending false
      return newMessage === false ? [] : [...previousMessages, newMessage];
    },
    []
  );

  const initialAppSettings = { volume: 1, isReview: false, isCoverPage: false };
  const [appSettings, setAppSettings] = React.useReducer(
    (prevSettings, newSettings) => Object.assign(prevSettings, newSettings),
    initialAppSettings
  );
  const [chatMode, setChatMode] = React.useState(CHAT_MODE.WAITING);

  function playNotifSound() {
    let audio = new Audio("./notif.mp3");
    audio.volume = appSettings.volume;
    audio.play();
  }

  function trackAgentName(agentName) {
    if (agentName !== undefined) {
      const previousAgents = taskContext.allAgentNames || {};
      const newAgent = { [agentId]: agentName };
      const allAgentNames = { ...previousAgents, ...newAgent };
      updateContext({ allAgentNames: allAgentNames });
    }
  }

  let mephistoProps = useMephistoLiveTask({
    onStateUpdate: ({ state, status }) => {
      trackAgentName(state.agent_display_name);
      if (state.task_done) {
        setChatMode(CHAT_MODE.DONE);
      } else if (
        [
          AGENT_STATUS.DISCONNECT,
          AGENT_STATUS.RETURNED,
          AGENT_STATUS.EXPIRED,
          AGENT_STATUS.TIMEOUT,
          AGENT_STATUS.MEPHISTO_DISCONNECT,
        ].includes(status)
      ) {
        setChatMode(CHAT_MODE.INACTIVE);
      } else if (state.wants_act) {
        setChatMode(CHAT_MODE.READY_FOR_INPUT);
        playNotifSound();
      }
    },
    onMessageReceived: (message) => {
      updateContext(message.task_data);
      addMessage(message);
    },
  });

  let {
    blockedReason,
    blockedExplanation,
    taskConfig,
    isPreview,
    previewHtml,
    isLoading,
    agentId,
    handleSubmit,
    connect,
    destroy,
    sendMessage,
    isOnboarding,
    agentState,
    agentStatus,
  } = mephistoProps;

  React.useEffect(() => {
    if (agentId) {
      console.log("connecting...");
      connect(agentId);
    }
  }, [agentId]);

  React.useEffect(() => {
    if (isOnboarding && agentStatus === AGENT_STATUS.WAITING) {
      handleSubmit();
    }
  }, [isOnboarding, agentStatus]);

  if (blockedReason !== null) {
    return <h1>{blockedExplanation}</h1>;
  }
  if (isLoading) {
    return <div>Initializing...</div>;
  }
  if (isPreview) {
    if (!taskConfig.has_preview) {
      return <TaskPreviewView description={taskConfig.task_description} />;
    }
    if (previewHtml === null) {
      return <div>Loading...</div>;
    }
    return <div dangerouslySetInnerHTML={{ __html: previewHtml }} />;
  }

  return (
    <MephistoContext.Provider
      value={{
        ...mephistoProps,
        chatMode,
        taskContext,
        appSettings,
        setAppSettings,
        allDoneCallback: () => {
          destroy();
          handleSubmit({});
        },
      }}
    >
      <div className="container-fluid" id="ui-container">
        <BaseFrontend
          messages={messages}
          onMessageSend={(message) => {
            message = {
              ...message,
              id: agentId,
              episode_done: agentState?.task_done || false,
            };
            return sendMessage(message)
              .then(addMessage)
              .then(() => setChatMode(CHAT_MODE.WAITING));
          }}
        />
      </div>
    </MephistoContext.Provider>
  );
}

function TaskPreviewView({ description }) {
  let previewStyle = {
    backgroundColor: "#dff0d8",
    padding: "30px",
    overflow: "auto",
  };
  return (
    <div style={previewStyle}>
      <div
        dangerouslySetInnerHTML={{
          __html: description,
        }}
      />
      ;
    </div>
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));
