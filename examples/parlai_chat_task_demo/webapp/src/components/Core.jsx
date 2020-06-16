/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";

import ReviewButtons from "./ReviewButtons.jsx";
import FormResponse from "./FormResponse.jsx";
import TextResponse from "./TextResponse.jsx";
import VolumeControl from "./VolumeControl.jsx";
import ConnectionIndicator from "./ConnectionIndicator.jsx";

import { MephistoContext, AppContext, INPUT_MODE } from "../app.jsx";
import { CONNECTION_STATUS } from "mephisto-task";

function ChatMessage({ is_self, duration, agent_name, message = "" }) {
  const floatToSide = is_self ? "right" : "left";
  const alertStyle = is_self ? "alert-info" : "alert-warning";

  return (
    <div className="row" style={{ marginLeft: "0", marginRight: "0" }}>
      <div
        className={"alert message " + alertStyle}
        role="alert"
        style={{ float: floatToSide }}
      >
        <span style={{ fontSize: "16px", whiteSpace: "pre-wrap" }}>
          <b>{agent_name}</b>: {message}
        </span>
        <ShowDuration duration={duration} />
      </div>
    </div>
  );
}

function ShowDuration({ duration }) {
  if (!duration) return null;

  const durationSeconds = Math.floor(duration / 1000) % 60;
  const durationMinutes = Math.floor(duration / 60000);
  const minutesText = durationMinutes > 0 ? `${durationMinutes} min` : "";
  const secondsText = durationSeconds > 0 ? `${durationSeconds} sec` : "";
  return (
    <small>
      <br />
      <i>Duration: </i>
      {minutesText + " " + secondsText}
    </small>
  );
}

function MessageList({ messages, onMessageClick }) {
  const { agentId } = React.useContext(MephistoContext);
  const {
    taskContext: { currentAgentNames },
    appSettings,
  } = React.useContext(AppContext);

  // Handles rendering messages from both the user and anyone else
  // on the thread - agent_ids for the sender of a message exist in
  // the m.id field.
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
            is_self={m.id === agentId || m.id in currentAgentNames}
            agent_name={
              m.id in currentAgentNames ? currentAgentNames[m.id] : m.id
            }
            message={m.text}
            task_data={m.task_data}
            message_id={m.message_id}
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

function Hourglass() {
  return (
    <div id="hourglass" className="hourglass-container">
      <span className="glyphicon glyphicon-hourglass" aria-hidden="true" />
    </div>
  );
}

function WaitingMessage({ agentStatus }) {
  let text = "Waiting for the next person to speak...";
  if (agentStatus === "waiting") {
    text = "Waiting to pair with a task...";
  }
  return (
    <div
      id="waiting-for-message"
      className="row"
      style={{ marginLeft: "0", marginRight: "0" }}
    >
      <div
        className="alert alert-warning message"
        role="alert"
        style={{
          backgroundColor: "#fff",
        }}
      >
        <Hourglass />
        <span style={{ fontSize: "16px" }}>{text}</span>
      </div>
    </div>
  );
}

function IdleResponse() {
  return <div id="response-type-idle" className="response-type-module" />;
}

function DoneButton({ displayFeedback = false }) {
  // This component is responsible for initiating the click
  // on the mturk form's submit button.
  const [showFeedback, setShowFeedback] = React.useState(displayFeedback);
  const [feedbackGiven, setFeedbackGiven] = React.useState(null);
  const { onTaskComplete } = React.useContext(AppContext);

  let review_flow = null;
  let done_button = (
    <button
      id="done-button"
      type="button"
      className="btn btn-primary btn-lg"
      onClick={() => onTaskComplete()}
    >
      <span className="glyphicon glyphicon-ok-circle" aria-hidden="true" /> Done
      with this HIT
    </button>
  );
  if (displayFeedback) {
    if (showFeedback) {
      review_flow = (
        <ReviewButtons
          initState={undefined}
          onMessageSend={onMessageSend}
          onChoice={(did_give) => {
            setShowFeedback(false);
            setFeedbackGiven(did_give);
          }}
        />
      );
      done_button = null;
    } else if (feedbackGiven) {
      review_flow = <span>Thanks for the feedback!</span>;
    }
  }
  return (
    <div>
      {review_flow}
      <div>{done_button}</div>
    </div>
  );
}

function DoneResponse({ onMessageSend }) {
  const { agentState = {} } = React.useContext(MephistoContext);
  const { done_text = null, task_done = null } = agentState;

  // TODO maybe move to CSS?
  let pane_style = {
    paddingLeft: "25px",
    paddingTop: "20px",
    paddingBottom: "20px",
    paddingRight: "25px",
    float: "left",
  };
  return (
    <div
      id="response-type-done"
      className="response-type-module"
      style={pane_style}
    >
      {done_text ? (
        <span id="inactive" style={{ fontSize: "14pt", marginRight: "15px" }}>
          {done_text}
        </span>
      ) : null}
      {task_done ? <DoneButton onMessageSend={onMessageSend} /> : null}
    </div>
  );
}

function CustomTaskDescription({ chatTitle, taskDescription }) {
  const { taskContext } = React.useContext(AppContext);

  return (
    <div>
      <h1>{chatTitle}</h1>
      <hr style={{ borderTop: "1px solid #555" }} />
      <h2>This is a custom Task Description loaded from a custom bundle</h2>
      <p>
        It has the ability to do a number of things, like directly access the
        contents of task data, view the number of messages so far, and pretty
        much anything you make like. We're also able to control other components
        as well, as in this example we've made it so that if you click a
        message, it will alert with that message idx.
      </p>
      <p>The current contents of task data are as follows: </p>
      <pre>{JSON.stringify(taskContext, null, 2)}</pre>
      <p>The regular task description content will now appear below:</p>
      <hr style={{ borderTop: "1px solid #555" }} />
      <span
        id="task-description"
        style={{ fontSize: "16px" }}
        dangerouslySetInnerHTML={{
          __html: taskDescription || "Task Description Loading",
        }}
      />
    </div>
  );
}

function LeftPane({ stretch = false, children }) {
  let pane_size = stretch ? "col-xs-12" : "col-xs-4";
  return <div className={pane_size + " left-pane"}>{children}</div>;
}

function RightPane({ children }) {
  return <div className="right-pane">{children}</div>;
}

function ChatPane({ messages, inputMode }) {
  const { agentStatus } = React.useContext(MephistoContext);

  const bottomAnchorRef = React.useRef(null);
  React.useEffect(() => {
    if (bottomAnchorRef.current) {
      bottomAnchorRef.current.scrollIntoView({
        block: "end",
        behavior: "smooth",
      });
    }
  }, [messages.length, inputMode]);

  return (
    <div className="right-top-pane">
      <ChatStatusBar />
      <div className="message-pane-segment">
        <MessageList messages={messages} />
        {inputMode === INPUT_MODE.WAITING ? (
          <WaitingMessage agentStatus={agentStatus} />
        ) : null}
        <div className="bottom-anchor" ref={bottomAnchorRef} />
      </div>
    </div>
  );
}

function ResponsePane({ onMessageSend, inputMode }) {
  const { taskContext } = React.useContext(AppContext);

  let response_pane = null;
  switch (inputMode) {
    case INPUT_MODE.DONE:
    case INPUT_MODE.INACTIVE:
      response_pane = <DoneResponse onMessageSend={onMessageSend} />;
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
      response_pane = <IdleResponse />;
      break;
  }

  return <div className="right-bottom-pane">{response_pane}</div>;
}

function BaseFrontend({ messages, onMessageSend, inputMode }) {
  const { connectionStatus, taskConfig } = React.useContext(MephistoContext);
  const { appSettings } = React.useContext(AppContext);

  if (connectionStatus === CONNECTION_STATUS.INITIALIZING) {
    return <div id="ui-placeholder">Initializing...</div>;
  } else if (connectionStatus === CONNECTION_STATUS.WEBSOCKETS_FAILURE) {
    return (
      <div id="ui-placeholder">
        Sorry, but we found that your browser does not support WebSockets.
        Please consider updating your browser to a newer version or using a
        different browser and check this HIT again.
      </div>
    );
  } else if (connectionStatus === CONNECTION_STATUS.FAILED) {
    return (
      <div id="ui-placeholder">
        Unable to initialize. We may be having issues with our servers. Please
        refresh the page, or if that isn't working return the HIT and try again
        later if you would like to work on this task.
      </div>
    );
  } else {
    return (
      <div
        className="row"
        id="ui-content"
        style={{ height: taskConfig.frame_height }}
      >
        <LeftPane stretch={appSettings.isCoverPage}>
          <CustomTaskDescription
            chatTitle={taskConfig.chat_title}
            taskDescription={taskConfig.task_description}
          />
        </LeftPane>
        <RightPane>
          <ChatPane inputMode={inputMode} messages={messages} />
          <ResponsePane inputMode={inputMode} onMessageSend={onMessageSend} />
        </RightPane>
      </div>
    );
  }
}

export {
  // Original Components
  ChatMessage,
  MessageList,
  ConnectionIndicator,
  Hourglass,
  WaitingMessage,
  ChatPane,
  IdleResponse,
  DoneButton,
  DoneResponse,
  ResponsePane,
  RightPane,
  LeftPane,
  BaseFrontend,
};
