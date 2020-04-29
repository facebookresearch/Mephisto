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

// props: mephisto_worker_id, agent_id, task_config, onboarding = False
class ChatApp extends React.Component {
  onMessageSend(text, data, callback, is_system) {
    if (text === "") {
      return;
    }
    this.socket_handler.handleQueueMessage(text, data, callback, is_system);
  }

  render() {
    return (
      <div>
        <BaseFrontend
          task_done={this.state.task_done}
          done_text={this.state.done_text}
          chat_state={this.state.chat_state}
          onMessageSend={(m, d, c, s) => this.onMessageSend(m, d, c, s)}
          socket_status={this.state.socket_status}
          messages={this.state.messages}
          agent_id={this.props.agent_id}
          agent_display_name={this.state.agent_display_name}
          task_description={this.props.task_config.task_description}
          chat_title={this.props.task_config.chat_title}
          initialization_status={this.state.initialization_status}
          frame_height={this.props.task_config.frame_height}
          task_data={this.state.task_data}
          world_state={this.state.agent_status}
          allDoneCallback={() => handleSubmit({})}
          volume={this.state.volume}
          onVolumeChange={(v) => this.setState({ volume: v })}
          display_feedback={false}
        />
        {socket_handler}
      </div>
    );
  }
}

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
    },
  });

  const [appState, setAppState] = React.useState({
    chat_state: "waiting", // idle, text_input, inactive, done
    messages: [],
    task_data: {},
    volume: 1, // min volume is 0, max is 1, TODO pull from local-storage?
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
      taskData={taskData}
      // agentState={agentState}
      onMessageSend={(data) => postData(data)}
      socket_status={serverStatus}
      messages={this.state.messages}
      agent_id={this.props.agent_id}
      agent_display_name={this.state.agent_display_name}
      task_description={this.props.task_config.task_description}
      chat_title={this.props.task_config.chat_title}
      initialization_status={this.state.initialization_status}
      frame_height={this.props.task_config.frame_height}
      task_data={this.state.task_data}
      world_state={this.state.agent_status}
      allDoneCallback={() => handleSubmit({})}
      volume={this.state.volume}
      onVolumeChange={(v) => this.setState({ volume: v })}
      display_feedback={false}
    />
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));
