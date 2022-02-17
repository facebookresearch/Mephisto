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
  SystemMessage,
  DoneResponse,
  ConnectionStatusBoundary,
  ChatPane,
} from "../index.js";
import { MephistoContext } from "mephisto-task";
import { AppContext, INPUT_MODE } from "./ChatApp.jsx";

function BaseFrontend({
  messages,
  onMessageSend,
  inputMode,
  renderSidePane,
  renderMessage,
  renderTextResponse,
  renderResponse,
}) {
  const mephistoContext = React.useContext(MephistoContext);
  const appContext = React.useContext(AppContext);

  const { connectionStatus, agentStatus, taskConfig } = mephistoContext;
  const { appSettings } = appContext;
  const sidePaneSize = appSettings.isCoverPage ? "col-xs-12" : "col-xs-4";
  const heightStyle =
    taskConfig.frame_height == 0 ? {} : { height: taskConfig.frame_height };

  return (
    <ConnectionStatusBoundary status={connectionStatus}>
      <div className="row" style={heightStyle}>
        <div className={"side-pane " + sidePaneSize}>
          {renderSidePane({ mephistoContext, appContext })}
        </div>
        <div className="chat-container-pane">
          <div className="right-top-pane">
            <ChatStatusBar />
            <ChatPane scrollBottomKey={messages.length + "-" + inputMode}>
              <div id="message_thread" style={{ width: "100%" }}>
                {messages.map((message, idx) =>
                  renderMessage({ message, idx, appContext, mephistoContext })
                )}
              </div>
              {inputMode === INPUT_MODE.WAITING ? (
                <SystemMessage
                  glyphicon="hourglass"
                  text={getWaitingMessage(agentStatus)}
                />
              ) : null}
            </ChatPane>
          </div>
          {renderResponse ? (
            renderResponse({
              onMessageSend,
              inputMode,
              appContext,
              mephistoContext,
            })
          ) : (
            <ResponsePane
              inputMode={inputMode}
              onMessageSend={onMessageSend}
              renderTextResponse={renderTextResponse}
            />
          )}
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

function ResponsePane({ onMessageSend, inputMode, renderTextResponse }) {
  const appContext = React.useContext(AppContext);
  const mephistoContext = React.useContext(MephistoContext);
  const { taskContext, onTaskComplete } = appContext;

  let response_pane = null;
  switch (inputMode) {
    case INPUT_MODE.DONE:
    case INPUT_MODE.INACTIVE:
      response_pane = (
        <DoneResponse
          onTaskComplete={onTaskComplete}
          onMessageSend={onMessageSend}
          doneText={taskContext.doneText || null}
          isTaskDone={taskContext.task_done || null}
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
        response_pane = renderTextResponse ? (
          renderTextResponse({
            onMessageSend,
            inputMode,
            active: inputMode === INPUT_MODE.READY_FOR_INPUT,
            appContext,
            mephistoContext,
          })
        ) : (
          <TextResponse
            onMessageSend={onMessageSend}
            active={inputMode === INPUT_MODE.READY_FOR_INPUT}
          />
        );
      }
      break;
    default:
      response_pane = null;
      break;
  }

  return <div className="right-bottom-pane">{response_pane}</div>;
}

export default BaseFrontend;
