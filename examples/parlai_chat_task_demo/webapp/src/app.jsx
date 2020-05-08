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

import {
  useMephistoLiveTask,
  getBlockedExplanation,
  AGENT_STATUS,
} from "mephisto-task";

/* global
  getWorkerName, getAssignmentId, getWorkerRegistrationInfo,
  getAgentRegistration, handleSubmitToProvider
*/

/* ================= Application Components ================= */

function TaskPreviewView({ taskConfig }) {
  let previewStyle = {
    backgroundColor: "#dff0d8",
    padding: "30px",
    overflow: "auto",
  };
  return (
    <div style={previewStyle}>
      <div
        dangerouslySetInnerHTML={{
          __html: taskConfig.task_description,
        }}
      />
      ;
    </div>
  );
}

function MainApp() {
  const [taskContext, updateContext] = React.useReducer(
    (oldContext, newContext) => Object.assign(oldContext, newContext),
    {}
  );

  const [messages, addMessage] = React.useReducer(
    (allMessages, newMessage) => [...allMessages, newMessage],
    []
  );

  const [appSettings, setAppSettings] = React.useState({ volume: 1 });
  const [chatState, setChatState] = React.useState("waiting");

  function playNotifSound() {
    let audio = new Audio("./notif.mp3");
    audio.volume = appSettings.volume;
    audio.play();
  }

  let {
    blockedReason,
    taskConfig,
    isPreview,
    isLoading,
    agentId,
    handleSubmit,
    connect,
    destroy,
    sendMessage,
    agentState,
    agentStatus,
    connectionStatus,
  } = useMephistoLiveTask({
    onStateUpdate: ({ state, status }) => {
      if (state.task_done) {
        setChatState("done");
      } else if (
        [
          AGENT_STATUS.DISCONNECT,
          AGENT_STATUS.RETURNED,
          AGENT_STATUS.EXPIRED,
          AGENT_STATUS.TIMEOUT,
          AGENT_STATUS.MEPHISTO_DISCONNECT,
        ].includes(status)
      ) {
        setChatState("inactive");
      } else if (state.wants_act) {
        setChatState("text_input");
        playNotifSound();
      }
    },
    onMessageReceived: (message) => {
      if (message.text === undefined) {
        message.text = "";
      }

      // Task data handling
      if (message.task_data !== undefined) {
        let has_context = false;
        for (let key of Object.keys(message.task_data)) {
          if (key !== "respond_with_form") {
            has_context = true;
          }
        }

        message.task_data.last_update = new Date().getTime();
        message.task_data.has_context = has_context;
        updateContext(message.task_data);
      }

      addMessage(message);
    },
  });

  React.useEffect(() => {
    if (agentId) {
      console.log("connecting...");
      connect(agentId);
    }
  }, [agentId]);

  if (blockedReason !== null) {
    return <h1>{getBlockedExplanation(blockedReason)}</h1>;
  }
  if (isLoading) {
    return <div>Initializing...</div>;
  }
  if (isPreview) {
    if (!taskConfig.has_preview) {
      return <TaskPreviewView taskConfig={taskConfig} />;
    }
    if (previewHtml === null) {
      return <div>Loading...</div>;
    }
    return <div dangerouslySetInnerHTML={{ __html: previewHtml }} />;
  }
  if (agentId === "onboarding") {
    // TODO handle the onboarding case
    return <div>Onboarding not yet implemented</div>;
  }
  return (
    <div>
      <BaseFrontend
        task_config={taskConfig}
        chat_state={chatState}
        agent_id={agentId}
        agent_status={agentStatus}
        agent_state={agentState || {}}
        connection_status={connectionStatus}
        task_data={taskContext} // TODO fix naming issues - taskData is the initial data for a task, task_context may change through a task
        messages={messages}
        onMessageSend={(message) => {
          message.id = agentId;
          message.episode_done = agentState?.task_done || false; 
          return sendMessage(message)
            .then((msg) => {
              addMessage(msg);
            })
            .then(() => setChatState("waiting"));
        }}
        allDoneCallback={() => {
          destroy();
          handleSubmit({});
        }}
        volume={appSettings.volume}
        onVolumeChange={(v) => setAppSettings({ volume: v })}
        display_feedback={false}
      />
    </div>
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));
