/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";
import ReactDOM from "react-dom";
import "bootstrap-chat/styles.css";
import "./style.css";
import CameraApp from "./components/CameraApp";

import { ChatApp, ChatMessage } from "bootstrap-chat";

import { Button, Popover, Overlay } from "react-bootstrap";
import Three from "three";

const MIN_UPDATE_TIME = 1000 / 10;

function MultimodalLeftPane({
  chatTitle,
  taskDescriptionHtml,
  onUpdateScenePos,
  currentPosition,
  canControlScene,
}) {
  const [showFullDescription, toggleDescription] = React.useState(false);

  const buttonRef = React.useRef();

  const toggleText = !showFullDescription
    ? "Show Description"
    : "Hide Description";
  const toggleButton = (
    <Button
      onClick={() => toggleDescription(!showFullDescription)}
      ref={(el) => {
        buttonRef.current = el;
      }}
    >
      {toggleText}
    </Button>
  );

  return (
    <div>
      <h1>
        {chatTitle} {toggleButton}
      </h1>
      <hr style={{ borderTop: "1px solid #555" }} />
      <Overlay
        rootClose
        show={showFullDescription}
        onHide={() => toggleDescription(false)}
        placement="bottom"
        target={buttonRef.current}
      >
        <Popover id="full_desc" title={"Full Task Description"}>
          <span
            id="task-description"
            style={{ fontSize: "16px" }}
            dangerouslySetInnerHTML={{
              __html: taskDescriptionHtml || "Task Description Loading",
            }}
          />
        </Popover>
      </Overlay>
      <CameraApp
        onUpdateScenePos={onUpdateScenePos}
        currentPosition={currentPosition}
        canControlScene={canControlScene}
      />
    </div>
  );
}

function RenderChatMessage({ message, mephistoContext, appContext }) {
  const { agentId } = mephistoContext;
  const { currentAgentNames } = appContext.taskContext;

  if (message.text.length == 0) {
    return null;
  }

  return (
    <ChatMessage
      isSelf={message.id === agentId}
      agentName={
        message.id in currentAgentNames
          ? currentAgentNames[message.id]
          : message.id
      }
      message={message.text}
      taskData={message.task_data}
      messageId={message.message_id}
    />
  );
}

function MephistoSimpleMessageApp() {
  const [messages, setMessages] = React.useState([]);
  const [lastSendTime, setLastSendTime] = React.useState(new Date().getTime());
  return (
    <ChatApp
      onMessagesChange={(newMessages) => setMessages(newMessages)}
      renderMessage={({ message, idx, mephistoContext, appContext }) => (
        <RenderChatMessage
          message={message}
          mephistoContext={mephistoContext}
          appContext={appContext}
          idx={idx}
          key={message.message_id + "-" + idx}
        />
      )}
      renderSidePane={({
        mephistoContext: { taskConfig, sendMessage, agentId },
        appContext: { taskContext },
      }) => (
        <MultimodalLeftPane
          chatTitle={taskConfig.chat_title}
          taskDescriptionHtml={taskConfig.task_description}
          currentPosition={taskContext.posArgs}
          canControlScene={taskContext.can_control_scene === true}
          onUpdateScenePos={(posArgs) => {
            let currTime = new Date().getTime();
            if (currTime - lastSendTime >= MIN_UPDATE_TIME) {
              setLastSendTime(currTime);
              let message = {
                text: "",
                task_data: {
                  update_position: true,
                  posArgs: posArgs,
                },
                id: agentId,
              };
              return sendMessage(message);
            }
          }}
        />
      )}
    />
  );
}

ReactDOM.render(<MephistoSimpleMessageApp />, document.getElementById("app"));
