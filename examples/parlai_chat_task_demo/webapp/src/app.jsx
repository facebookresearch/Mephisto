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

/* ================= Agent State Constants ================= */

// TODO move to shared file
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

/* ================= Application Components ================= */

// props: mephisto_worker_id, agent_id, task_config, onboarding = False
class ChatApp extends React.Component {
  constructor(props) {
    super(props);

    // TODO move constants to props rather than state
    this.state = {
      initialization_status: "initializing",
      socket_status: null, // TODO improve this functionality for disconnects
      agent_status: STATUS_WAITING, // TODO, start as STATUS_NONE when implementing onboarding
      done_text: null,
      chat_state: "waiting", // idle, text_input, inactive, done
      task_done: false,
      messages: [],
      task_data: {},
      volume: 1, // min volume is 0, max is 1, TODO pull from local-storage?
    };
  }

  // TODO implement?
  handleAgentStatusChange(agent_status, display_name, done_text) {
    console.log("Handling state update", agent_status, this.state.agent_status);
    if (agent_status != this.state.agent_status) {
      // Handle required state changes on a case-by-case basis.
      if ([STATUS_DONE, STATUS_PARTNER_DISCONNECT].includes(agent_status)) {
        this.setState({ task_done: true, chat_state: "done" });
        this.socket_handler.closeSocket();
      } else if (
        [
          STATUS_DISCONNECT,
          STATUS_RETURNED,
          STATUS_EXPIRED,
          STATUS_TIMEOUT,
          STATUS_MEPHISTO_DISCONNECT,
        ].includes(agent_status)
      ) {
        this.setState({ chat_state: "inactive", done_text: done_text });
        this.socket_handler.closeSocket();
      } else if (agent_status == STATUS_WAITING) {
        this.setState({ messages: [], chat_state: "waiting" });
      }
      this.setState({ agent_status: agent_status, done_text: done_text });
    }
    if (display_name != this.state.agent_display_name) {
      this.setState({ agent_display_name: display_name });
    }
  }

  playNotifSound() {
    let audio = new Audio("./notif.mp3");
    audio.volume = this.state.volume;
    audio.play();
  }

  handleIncomingTaskData(taskData) {
    console.log("Got task data", taskData);
    this.setState({ task_data: taskData.task_data });
    let messages = taskData.raw_messages;
    for (const message of messages) {
      this.socket_handler.parseSocketMessage(message);
    }
  }

  componentDidMount() {
    this.handleIncomingTaskData(this.props.taskData);
  }

  onMessageSend(text, data, callback, is_system) {
    if (text === "") {
      return;
    }
    this.socket_handler.handleQueueMessage(text, data, callback, is_system);
  }

  render() {
    let socket_handler = null;
    socket_handler = (
      <SocketHandler
        onNewMessage={(new_message) => {
          this.state.messages.push(new_message);
          this.setState({ messages: this.state.messages });
        }}
        onNewTaskData={(new_task_data) =>
          this.setState({
            task_data: Object.assign(this.state.task_data, new_task_data),
          })
        }
        onRequestMessage={() => this.setState({ chat_state: "text_input" })}
        onForceDone={() => this.props.handleSubmit(this.state.messages)}
        onSuccessfulSend={() =>
          this.setState({
            chat_state: "waiting",
            messages: this.state.messages,
          })
        }
        onAgentStatusChange={(agent_status, display_name, done_text) =>
          this.handleAgentStatusChange(agent_status, display_name, done_text)
        }
        agent_display_name={this.state.agent_display_name}
        onConfirmInit={() => this.setState({ initialization_status: "done" })}
        onFailInit={() => this.setState({ initialization_status: "failed" })}
        onStatusChange={(status) => this.setState({ socket_status: status })}
        agent_id={this.props.agent_id}
        initialization_status={this.state.initialization_status}
        agent_status={this.state.agent_status}
        messages={this.state.messages}
        task_done={this.state.task_done}
        ref={(m) => {
          this.socket_handler = m;
        }}
        playNotifSound={() => this.playNotifSound()}
      />
    );
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
          allDoneCallback={() =>
            postCompleteTask(
              this.props.agent_id,
              this.state.messages
            ).then(() => handleSubmitToProvider({}))
          }
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
  let {
    blockedReason,
    taskConfig,
    taskData,
    isPreview,
    agentId,
    mephistoWorkerId,
    handleSubmit,
  } = useMephistoTask();

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
    <ChatApp
      task_config={taskConfig}
      agent_id={agentId}
      mephisto_worker_id={mephistoWorkerId}
      onSubmit={handleSubmit}
      taskData={taskData}
    />
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));
