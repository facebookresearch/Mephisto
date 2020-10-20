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

function loadDifferentPassage(e, handlePassageIdSend) {
  if (e.target.tagName == "SPAN") {
    handlePassageIdSend(e.target.id)
  }

}

function RenderPassage({ setTextValue, handlePassageIdSend, passage }) {
  const mystyle = {
    resize: "none",
    backgroundColor: "#dff0d8",
    width: "100%",
    height: "100%",
    border: "0px"
  };

  // return (<textarea readOnly style={mystyle} onSelect={(e) => logSelection(e, setTextValue)} defaultValue={passage} />)

  return (<p onClick={(e) => loadDifferentPassage(e, handlePassageIdSend)} dangerouslySetInnerHTML={{ __html: passage }} />)
}

function RenderChatMessage({ message, mephistoContext, appContext, idx }) {
  const { agentId } = mephistoContext;
  const { currentAgentNames } = appContext.taskContext;
  if ('text' in message) {
    return (
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
  return null
}

function MainApp() {

  const [passage, setPassage] = React.useState("");

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
      renderSidePane={({ mephistoContext: { taskConfig }, textValue, setTextValue, handlePassageIdSend }) => (
        <DefaultTaskDescription
          chatTitle={taskConfig.chat_title}
          taskDescriptionHtml={taskConfig.task_description}
        >
          <RenderPassage setTextValue={setTextValue} handlePassageIdSend={handlePassageIdSend} passage={passage} />
        </DefaultTaskDescription>
      )}
      onMessagesChange={(messages) => {
        if (messages.length > 0 && 'passage' in messages[messages.length - 1]) {
          setPassage(messages[messages.length - 1].passage)
        }
      }}
    />
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));

