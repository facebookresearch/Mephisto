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
  STATUS,
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
  const [volume, setVolume] = React.useState(1);
  const [taskContext, updateContext] = React.useReducer(
    (oldContext, newContext) => Object.assign(oldContext, newContext),
    {}
  );

  const [messages, addMessage] = React.useReducer(
    (allMessages, newMessage) => [...allMessages, newMessage],
    []
  );

  const [appState, setAppState] = React.useState({ volume: 1 });
  const [chatState, setChatState] = React.useState("waiting");

  function playNotifSound() {
    let audio = new Audio("./notif.mp3");
    audio.volume = volume;
    audio.play();
  }

  let {
    blockedReason,
    taskConfig,
    taskData,
    isPreview,
    isLoading,
    agentId,
    mephistoWorkerId,
    handleSubmit,
    connect,
    sendMessage,
    agentState,
    agentStatus,
    connectionStatus,
  } = useMephistoLiveTask({
    onStateUpdate: ({ state, status }) => {
      console.log(`[Event] State updated. [Status: ${status}]`);
      console.table(state);

      if (state.task_done) {
        setChatState("done");
      } else if (
        [
          STATUS.STATUS_DISCONNECT,
          STATUS.STATUS_RETURNED,
          STATUS.STATUS_EXPIRED,
          STATUS.STATUS_TIMEOUT,
          STATUS.STATUS_MEPHISTO_DISCONNECT,
        ].includes(status)
      ) {
        setChatState("inactive");
      } else if (state.wants_act) {
        setChatState("text_input");
        playNotifSound();
      }
    },
    onMessageReceived: (message) => {
      console.log(`[Event] Message received`);

      const { task_data, ...messageProps } = message;
      console.table(messageProps);
      console.table(task_data);

      if (message.text === undefined) {
        message.text = "";
      }
      addMessage(message);

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
      {/* <InsertRequiredSocketComponent /> */}
      <BaseFrontend
        task_config={taskConfig}
        chat_state={chatState}
        agent_id={agentId}
        mephisto_worker_id={mephistoWorkerId}
        onSubmit={handleSubmit}
        done_text={agentState?.done_text} // TODO: remove after agentState refactor
        task_done={agentState?.task_done} // TODO: remove after agentState refactor
        agent_display_name={agentState?.agent_display_name} // TODO: remove after agentState refactor
        taskData={taskData}
        task_data={taskContext} // TODO fix naming issues - taskData is the initial data for a task, task_context may change through a task
        // agentState={agentState}
        onMessageSend={(text, task_data) => {
          console.log(`[Event] Message sent`);
          console.table(task_data);
          return sendMessage(text, task_data)
            .then((msg) => {
              addMessage(msg);
            })
            .then(() => setChatState("waiting"));
        }} // TODO we're using a slightly different format, need to package ourselves
        socket_status={connectionStatus} // TODO coalesce with the initialization status
        messages={messages}
        agent_id={agentId}
        task_description={taskConfig.task_description} // TODO coalescs taskConfig
        frame_height={taskConfig.frame_height} // TODO coalescs taskConfig
        chat_title={taskConfig.chat_title} // TODO coalescs taskConfig
        initialization_status={connectionStatus} // TODO remove and just have one server status
        world_state={agentStatus}
        allDoneCallback={() => handleSubmit({})}
        volume={appState.volume}
        onVolumeChange={(v) => setAppState({ volume: v })}
        display_feedback={false}
      />
    </div>
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));
