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
import SocketHandler from "./components/socket_handler.jsx";

import {
  useMephistoTask,
  getBlockedExplanation,
  doesSupportWebsockets,
} from "mephisto-task";

// setCustomComponents(UseCustomComponents);

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
  const [appState, setAppState] = React.useState({
    chat_state: "waiting", // idle, text_input, inactive, done
    task_data: {},
    volume: 1, // min volume is 0, max is 1, TODO pull from local-storage?
  });

  function playNotifSound() {
    let audio = new Audio("./notif.mp3");
    audio.volume = appState.volume;
    audio.play();
  }

  const [messages, addMessage] = React.useReducer(
    (allMessages, newMessage) => [...allMessages, newMessage],
    []
  );

  let {
    blockedReason,
    taskConfig,
    taskData,
    isPreview,
    agentId,
    mephistoWorkerId,
    handleSubmit,
    agentStatus,
    agentState,
    postData,
    serverStatus, // lo pris
  } = useMephistoLiveTask({
    onNewData: (newData) => {
      addMessage(newData);
      // and more!
      // Determine the type of newData package - action request or an action

      // if request act type:
      //   // // Handle incoming command messages
      //   // handleRequestAct(msg) {
      //   //   // Update UI to wait for the worker to submit a message
      //   //   this.props.onRequestMessage();
      //   //   if (this.state.message_request_time === null) {
      //   //     this.props.playNotifSound();
      //   //   }
      //   //   this.setState({ message_request_time: new Date().getTime() });
      //   //   log('Waiting for worker input', 4);
      //   // }
      // else:
      //   addMessage(newData);
      //   if (message.text === undefined) {
      //     message.text = '';
      //   }
    
      //   this.props.onNewMessage(message);
    
      //   // Handle special case of receiving own sent message
      //   if (message.id == this.props.agent_id) {
      //     this.props.onSuccessfulSend();
      //   }
    
      //   // Task data handling
      //   if (message.task_data !== undefined) {
      //     let has_context = false;
      //     for (let key of Object.keys(message.task_data)) {
      //       if (key !== 'respond_with_form') {
      //         has_context = true;
      //       }
      //     }
    
      //     message.task_data.last_update = new Date().getTime();
      //     message.task_data.has_context = has_context;
      //     this.props.onNewTaskData(message.task_data);
      //   }
      // },
  });


  // TODO: move to useMephistoLiveTask
  if (!doesSupportWebsockets()) {
    blockedReason = "no_websockets";
  }

  if (blockedReason !== null) {
    return <h1>{getBlockedExplanation(blockedReason)}</h1>;
  }
  if (taskConfig === null) {
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
  if (agentId === null) {
    return <div>Initializing...</div>;
  }
  if (agentId === "onboarding") {
    // TODO handle the onboarding case
    return <div>Onboarding not yet implemented</div>;
  }
  return (
    <BaseFrontend
      task_config={taskConfig}
      agent_id={agentId}
      mephisto_worker_id={mephistoWorkerId}
      onSubmit={handleSubmit}
      done_text={agentState.done_text} // TODO: remove after agentState refactor
      task_done={agentState.task_done} // TODO: remove after agentState refactor
      agent_display_name={agentState.agent_display_name} // TODO: remove after agentState refactor
      task_data={taskData}
      // agentState={agentState}
      onMessageSend={(data) => postData(data)} // TODO we're using a slightly different format, need to package ourselves
      socket_status={serverStatus} // TODO coalesce with the initialization status
      messages={messages}
      agent_id={agentId}
      task_description={taskConfig.task_description} // TODO coalescs taskConfig
      frame_height={taskConfig.frame_height} // TODO coalescs taskConfig
      chat_title={taskConfig.chat_title} // TODO coalescs taskConfig
      initialization_status={serverStatus} // TODO remove and just have one server status
      world_state={agentStatus}
      allDoneCallback={() => handleSubmit({})}
      volume={appState.volume}
      onVolumeChange={(v) => setAppState({ ...appState, volume: v })}
      display_feedback={false}
    />
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));
