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
import { FormGroup, FormControl, Button, Radio } from "react-bootstrap";

import { ChatApp, DefaultTaskDescription, INPUT_MODE } from "bootstrap-chat";

/*
This example modifies the default parlai_chat example to demonstrate
how one can override the default visual implementations for the
chat message bubble and the response input bar, while coordinating
behavior between them with global state.

In this example we add a radio button group to each received chat message.
Additionally, we require the user to make a selection for the most
recently received chat message, before they can submit their own message
by modifying the input bar code.

This example is for illustrative purposes only and has not been tested
with production usage.
*/

function ChatMessage({ isSelf, idx, agentName, message = "", onRadioChange }) {
  const floatToSide = isSelf ? "right" : "left";
  const alertStyle = isSelf ? "alert-info" : "alert-warning";

  const handleChange = (e) => {
    onRadioChange(e.currentTarget.value);
  };

  return (
    <div className="row" style={{ marginLeft: "0", marginRight: "0" }}>
      <div
        className={"alert message " + alertStyle}
        role="alert"
        style={{ float: floatToSide }}
      >
        <span style={{ fontSize: "16px", whiteSpace: "pre-wrap" }}>
          <b>{agentName}</b>: {message}
        </span>
        {isSelf ? null : (
          <FormGroup>
            <Radio
              name={"radio" + idx}
              value={1}
              inline
              onChange={handleChange}
            >
              1
            </Radio>{" "}
            <Radio
              name={"radio" + idx}
              value={2}
              inline
              onChange={handleChange}
            >
              2
            </Radio>{" "}
          </FormGroup>
        )}
      </div>
    </div>
  );
}

function RenderChatMessage({
  message,
  mephistoContext,
  appContext,
  idx,
  onRadioChange,
}) {
  const { agentId } = mephistoContext;
  const { currentAgentNames } = appContext.taskContext;

  return (
    <div>
      <ChatMessage
        idx={idx}
        isSelf={message.id === agentId || message.id in currentAgentNames}
        agentName={
          message.id in currentAgentNames
            ? currentAgentNames[message.id]
            : message.id
        }
        message={message.text}
        taskData={message.task_data}
        messageId={message.update_id}
        onRadioChange={onRadioChange}
      />
    </div>
  );
}

function MainApp() {
  const [messages, setMessages] = React.useState([]);
  const [chatAnnotations, setChatAnnotation] = React.useReducer(
    (state, action) => {
      return { ...state, ...{ [action.index]: action.value } };
    },
    {}
  );

  const lastMessageAnnotation = chatAnnotations[messages.length - 1];

  return (
    <ChatApp
      onMessagesChange={(messages) => {
        setMessages(messages);
      }}
      /*
        You can also use renderTextResponse below, which allows you
        to modify the input bar while keeping additional default
        functionality such as the ability to trigger custom forms
        and a done state.
        Or you can use renderResponse for more flexibility and implement
        those states yourself, as shown below with the done state:
      */
      renderResponse={({ onMessageSend, inputMode, appContext }) =>
        inputMode === INPUT_MODE.DONE ? (
          <div className="response-type-module">
            <div className="response-bar">
              <h3>Thanks for completing the task!</h3>
              <button
                id="done-button"
                type="button"
                className="btn btn-primary btn-lg"
                onClick={() => appContext.onTaskComplete()}
              >
                <span
                  className="glyphicon glyphicon-ok-circle"
                  aria-hidden="true"
                />{" "}
                Done with this HIT
              </button>
            </div>
          </div>
        ) : (
          <CustomTextResponse
            onMessageSend={onMessageSend}
            active={inputMode === INPUT_MODE.READY_FOR_INPUT}
            messages={messages}
            key={lastMessageAnnotation}
            isLastMessageAnnotated={
              messages.length === 0 || lastMessageAnnotation !== undefined
            }
            lastMessageAnnotation={lastMessageAnnotation}
          />
        )
      }
      renderMessage={({ message, idx, mephistoContext, appContext }) => (
        <RenderChatMessage
          message={message}
          mephistoContext={mephistoContext}
          appContext={appContext}
          idx={idx}
          key={message.update_id + "-" + idx}
          onRadioChange={(val) => {
            setChatAnnotation({ index: idx, value: val });
          }}
        />
      )}
      renderSidePane={({ mephistoContext: { taskConfig } }) => (
        <DefaultTaskDescription
          chatTitle={taskConfig.chat_title}
          taskDescriptionHtml={taskConfig.task_description}
        >
          <h2>This is a custom Task Description loaded from a custom bundle</h2>
          <p>
            It has the ability to do a number of things, like directly access
            the contents of task data, view the number of messages so far, and
            pretty much anything you make like. We're also able to control other
            components as well, as in this example we've made it so that if you
            click a message, it will alert with that message idx.
          </p>
          <p>The regular task description content will now appear below:</p>
        </DefaultTaskDescription>
      )}
    />
  );
}

function CustomTextResponse({
  onMessageSend,
  active,
  isLastMessageAnnotated,
  lastMessageAnnotation,
}) {
  const [textValue, setTextValue] = React.useState(
    !lastMessageAnnotation ? "" : lastMessageAnnotation + " - "
  );
  const [sending, setSending] = React.useState(false);

  const annotationNeeded = active && !isLastMessageAnnotated;
  active = active && isLastMessageAnnotated;

  const inputRef = React.useRef();

  React.useEffect(() => {
    if (active && inputRef.current && inputRef.current.focus) {
      inputRef.current.focus();
    }
  }, [active]);

  const tryMessageSend = React.useCallback(() => {
    if (textValue !== "" && active && !sending) {
      setSending(true);
      onMessageSend({ text: textValue, task_data: {} }).then(() => {
        setTextValue("");
        setSending(false);
      });
    }
  }, [textValue, active, sending, onMessageSend]);

  const handleKeyPress = React.useCallback(
    (e) => {
      if (e.key === "Enter") {
        tryMessageSend();
        e.stopPropagation();
        e.nativeEvent.stopImmediatePropagation();
      }
    },
    [tryMessageSend]
  );

  return (
    <div className="response-type-module">
      <div className="response-bar">
        <FormControl
          type="text"
          className="response-text-input"
          inputRef={(ref) => {
            inputRef.current = ref;
          }}
          value={textValue}
          placeholder={
            annotationNeeded
              ? "Please annotate the last message before you can continue"
              : "Enter your message here..."
          }
          onKeyPress={(e) => handleKeyPress(e)}
          onChange={(e) => setTextValue(e.target.value)}
          disabled={!active || sending}
        />
        <Button
          className="btn btn-primary submit-response"
          id="id_send_msg_button"
          disabled={textValue === "" || !active || sending}
          onClick={() => tryMessageSend()}
        >
          Send
        </Button>
      </div>
    </div>
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));
