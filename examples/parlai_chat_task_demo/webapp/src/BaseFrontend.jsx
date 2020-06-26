/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";
import {
  ConnectionIndicator,
  FormResponse,
  TextResponse,
  VolumeControl,
  ChatMessage,
  SystemMessage,
  DoneResponse,
  ConnectionStatusBoundary,
  DefaultTaskDescription,
  ChatPane,
} from "bootstrap-chat";
import { MephistoContext } from "mephisto-task";
import { AppContext, INPUT_MODE } from "./app.jsx";

function BaseFrontend({ messages, onMessageSend, inputMode }) {
  const { connectionStatus, agentStatus, taskConfig } = React.useContext(
    MephistoContext
  );
  const { appSettings, taskContext } = React.useContext(AppContext);
  const sidePaneSize = appSettings.isCoverPage ? "col-xs-12" : "col-xs-4";

  return (
    <ConnectionStatusBoundary status={connectionStatus}>
      <div className="row" style={{ height: taskConfig.frame_height }}>
        <div className={"side-pane " + sidePaneSize}>
          <DefaultTaskDescription
            chatTitle={taskConfig.chat_title}
            taskDescription={taskConfig.task_description}
            taskContext={taskContext}
          >
            <h2>
              This is a custom Task Description loaded from a custom bundle
            </h2>
            <p>
              It has the ability to do a number of things, like directly access
              the contents of task data, view the number of messages so far, and
              pretty much anything you make like. We're also able to control
              other components as well, as in this example we've made it so that
              if you click a message, it will alert with that message idx.
            </p>
            <p>The regular task description content will now appear below:</p>
          </DefaultTaskDescription>
        </div>
        <div className="chat-container-pane">
          <div className="right-top-pane">
            <ChatStatusBar />
            <ChatPane scrollBottomKey={messages.length + "-" + inputMode}>
              <MessageList messages={messages} />
              {inputMode === INPUT_MODE.WAITING ? (
                <SystemMessage
                  glyphicon="hourglass"
                  text={getWaitingMessage(agentStatus)}
                />
              ) : null}
            </ChatPane>
          </div>
          <ResponsePane inputMode={inputMode} onMessageSend={onMessageSend} />
        </div>
      </div>
    </ConnectionStatusBoundary>
  );
}

function getWaitingMessage(agentStatus) {
  return agentStatus === "waiting"
    ? "Waiting to pair with a task..."
    : "Waiting for the next person to speak...";
}

function MessageList({ messages, onMessageClick }) {
  const { agentId } = React.useContext(MephistoContext);
  const { taskContext, appSettings } = React.useContext(AppContext);
  const { currentAgentNames } = taskContext;

  if (typeof onMessageClick !== "function") {
    onMessageClick = (idx) => {
      alert("You've clicked on message number: " + idx);
    };
  }

  return (
    <div id="message_thread" style={{ width: "100%" }}>
      {messages.map((m, idx) => (
        <div key={m.message_id + "-" + idx} onClick={() => onMessageClick(idx)}>
          <ChatMessage
            isSelf={m.id === agentId || m.id in currentAgentNames}
            agentName={
              m.id in currentAgentNames ? currentAgentNames[m.id] : m.id
            }
            message={m.text}
            taskData={m.task_data}
            messageId={m.message_id}
            duration={appSettings.isReview ? m.duration : undefined}
          />
        </div>
      ))}
    </div>
  );
}

function ChatStatusBar() {
  const { connectionStatus } = React.useContext(MephistoContext);
  const { appSettings, setAppSettings } = React.useContext(AppContext);

  return (
    <div className="chat-status-bar">
      <ConnectionIndicator connectionStatus={connectionStatus} />
      <VolumeControl
        volume={appSettings.volume}
        onVolumeChange={(v) => setAppSettings({ volume: v })}
      />
    </div>
  );
}

function ResponsePane({ onMessageSend, inputMode }) {
  const { taskContext, onTaskComplete } = React.useContext(AppContext);
  const { agentState = {} } = React.useContext(MephistoContext);

  let response_pane = null;
  switch (inputMode) {
    case INPUT_MODE.DONE:
    case INPUT_MODE.INACTIVE:
      response_pane = (
        <DoneResponse
          onTaskComplete={onTaskComplete}
          onMessageSend={onMessageSend}
          doneText={agentState.done_text || null}
          isTaskDone={agentState.task_done || null}
        />
      );
      break;
    case INPUT_MODE.READY_FOR_INPUT:
    case INPUT_MODE.WAITING:
      if (taskContext && taskContext["respond_with_form"]) {
        response_pane = (
          <FormResponse
            onMessageSend={onMessageSend}
            active={inputMode === INPUT_MODE.READY_FOR_INPUT}
            formOptions={taskContext["respond_with_form"]}
          />
        );
      } else {
        response_pane = (
          <TextResponse
            onMessageSend={onMessageSend}
            active={inputMode === INPUT_MODE.READY_FOR_INPUT}
          />
        );
      }
      break;
    case INPUT_MODE.IDLE:
    default:
      response_pane = null;
      break;
  }

  return <div className="right-bottom-pane">{response_pane}</div>;
}

export default BaseFrontend;
