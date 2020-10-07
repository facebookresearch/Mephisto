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

import { ChatApp, ChatMessage, DefaultTaskDescription } from "../../../../packages/bootstrap-chat";

function logSelection(event, setTextValue) {
  const selection = event.target.value.substring(event.target.selectionStart, event.target.selectionEnd);
  console.log(selection)
  setTextValue(selection)
  // debugger
}

function TestingFunction({ messages, setTextValue }) {
  const mystyle = {
    resize: "none",
    backgroundColor: "#dff0d8",
    width: "100%",
    height: "100%",
    border: "0px"
  };
  if (messages.length > 0) {
    return (<textarea readOnly style={mystyle} onSelect={(e) => logSelection(e, setTextValue)} defaultValue={messages[0].passage} />)
  }
  return null
}

// function TestHighlight({ text }) {
//   // console.log("Some text has been highlighted")
//   return (<p> {text} </p>)
// }

function RenderChatMessage({ message, mephistoContext, appContext, idx }) {
  const { agentId } = mephistoContext;
  const { currentAgentNames } = appContext.taskContext;

  return (
    // <div onClick={() => alert("You clicked on message with index " + idx)}>
    <div>
      <ChatMessage
        isSelf={message.id === agentId || message.id in currentAgentNames}
        agentName={
          message.id in currentAgentNames
            ? currentAgentNames[message.id]
            : message.id
        }
        message={message.text}
        taskData={message.task_data}
        messageId={message.message_id}
      />
    </div>
  );
}

function MainApp() {
  return (
    <ChatApp
      renderMessage={({ message, idx, mephistoContext, appContext }) => (
        <RenderChatMessage
          message={message}
          mephistoContext={mephistoContext}
          appContext={appContext}
          idx={idx}
          key={message.message_id + "-" + idx}
        />
      )}
      renderSidePane={({ mephistoContext: { taskConfig }, messages, textValue, setTextValue }) => (
        <DefaultTaskDescription
          chatTitle={taskConfig.chat_title}
          taskDescriptionHtml={taskConfig.task_description}
        >
          <TestingFunction messages={messages} setTextValue={setTextValue} />
          {/* <TestHighlight text={window.getSelection().toString()} /> */}
        </DefaultTaskDescription>
      )}
    />
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));

