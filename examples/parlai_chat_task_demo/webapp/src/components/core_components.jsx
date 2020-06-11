/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";
import { FormControl, Button } from "react-bootstrap";
import ReviewButtons from "./ReviewButtons.jsx";
import FormResponse from "./FormResponse.jsx";
import VolumeControl from "./VolumeControl.jsx";
import ConnectionIndicator from "./ConnectionIndicator.jsx";

import { MephistoContext, CHAT_MODE } from "../app.jsx";

import $ from "jquery";
import { CONNECTION_STATUS } from "mephisto-task";

/*
  REMOVED:
  Tabbed navigation view option for context. Context now just shown in the left bar w/ description instead of separate tab
  ContextView component
  All the resize stuff
  Got rid of display_feedback from BaseFrontend
*/

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

function ChatMessage({ is_self, duration, agent_id, message = "" }) {
  const floatToSide = is_self ? "right" : "left";
  const alertStyle = is_self ? "alert-info" : "alert-warning";

  return (
    <div className={"row"} style={{ marginLeft: "0", marginRight: "0" }}>
      <div
        className={"alert " + alertStyle}
        role="alert"
        style={{ float: floatToSide, display: "table" }}
      >
        <span style={{ fontSize: "16px", whiteSpace: "pre-wrap" }}>
          <b>{agent_id}</b>: {message}
        </span>
        <ShowDuration duration={duration} />
      </div>
    </div>
  );
}

function MessageList({ messages, onClickMessage }) {
  const {
    agentId,
    taskContext: { allAgentNames },
    appSettings,
  } = React.useContext(MephistoContext);

  // Handles rendering messages from both the user and anyone else
  // on the thread - agent_ids for the sender of a message exist in
  // the m.id field.
  if (typeof onClickMessage !== "function") {
    onClickMessage = (idx) => {
      alert("You've clicked on message number: " + idx);
    };
  }
  return (
    <div id="message_thread" style={{ width: "100%" }}>
      {messages.map((m, idx) => (
        <div key={m.message_id + "-" + idx} onClick={() => onClickMessage(idx)}>
          <ChatMessage
            is_self={m.id === agentId || m.id in allAgentNames}
            agent_id={m.id in allAgentNames ? allAgentNames[m.id] : m.id}
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

function ChatStatusBar({ displayWorkerChatPopup = false }) {
  const { appSettings, setAppSettings, connectionStatus } = React.useContext(
    MephistoContext
  );

  let nav_style = {
    position: "absolute",
    backgroundColor: "#EEEEEE",
    borderColor: "#e7e7e7",
    height: 46,
    top: 0,
    borderWidth: "0 0 1px",
    borderRadius: 0,
    right: 0,
    left: 0,
    zIndez: 1030,
    padding: 5,
  };
  return (
    <div style={nav_style}>
      <ConnectionIndicator connectionStatus={connectionStatus} />
      <VolumeControl
        volume={appSettings.volume}
        onVolumeChange={(v) => setAppSettings({ volume: v })}
      />
      {/* displayWorkerChatPopup && (
        <WorkerChatPopup
          off_chat_messages={chatMessages}
          onMessageSend={(msg) =>
            setChatMessages([...chatMessages, { msg, owner: 0 }])
          }
          has_new_message={2}
        />
      ) */}
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
  let message_style = {
    float: "left",
    display: "table",
    backgroundColor: "#fff",
  };
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
      <div className="alert alert-warning" role="alert" style={message_style}>
        <Hourglass />
        <span style={{ fontSize: "16px" }}>{text}</span>
      </div>
    </div>
  );
}

function ChatPane({ messages }) {
  const { chatMode, agentStatus } = React.useContext(MephistoContext);

  // TODO move to CSS
  let top_pane_style = {
    width: "100%",
    position: "relative",
    // height: this.state.chat_height + "px",
  };

  let chat_style = {
    width: "100%",
    // height: this.state.chat_height + "px",
    paddingTop: "60px",
    paddingLeft: "20px",
    paddingRight: "20px",
    paddingBottom: "20px",
    overflowY: "scroll",
  };

  return (
    <div id="right-top-pane" style={top_pane_style}>
      <ChatStatusBar />
      <div id="message-pane-segment" style={chat_style}>
        <MessageList messages={messages} />
        {chatMode === CHAT_MODE.WAITING ? (
          <WaitingMessage agentStatus={agentStatus} />
        ) : null}
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
  const { allDoneCallback, onMessageSend } = React.useContext(MephistoContext);

  let review_flow = null;
  let done_button = (
    <button
      id="done-button"
      type="button"
      className="btn btn-primary btn-lg"
      onClick={() => allDoneCallback()}
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

function DoneResponse() {
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
      {task_done ? <DoneButton /> : nulls}
    </div>
  );
}

class TextResponse extends React.Component {
  constructor(props) {
    super(props);
    this.state = { textval: "", sending: false };
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    // Only change in the active status of this component should cause a
    // focus event. Not having this would make the focus occur on every
    // state update (including things like volume changes)
    if (this.props.active && !prevProps.active) {
      $("input#id_text_input").focus();
    }
    // this.props.onInputResize();
  }

  tryMessageSend() {
    if (this.state.textval !== "" && this.props.active && !this.state.sending) {
      this.setState({ sending: true });
      this.props
        .onMessageSend({ text: this.state.textval, task_data: {} })
        .then(() => this.setState({ textval: "", sending: false }));
    }
  }

  handleKeyPress(e) {
    if (e.key === "Enter") {
      this.tryMessageSend();
      e.stopPropagation();
      e.nativeEvent.stopImmediatePropagation();
    }
  }

  render() {
    // TODO maybe move to CSS?
    let pane_style = {
      paddingLeft: "25px",
      paddingTop: "20px",
      paddingBottom: "20px",
      paddingRight: "25px",
      float: "left",
      width: "100%",
    };
    let input_style = {
      height: "50px",
      width: "100%",
      display: "block",
      float: "left",
    };
    let submit_style = {
      width: "100px",
      height: "100%",
      fontSize: "16px",
      float: "left",
      marginLeft: "10px",
      padding: "0px",
    };

    let text_input = (
      <FormControl
        type="text"
        id="id_text_input"
        style={{
          width: "80%",
          height: "100%",
          float: "left",
          fontSize: "16px",
        }}
        value={this.state.textval}
        placeholder="Please enter here..."
        onKeyPress={(e) => this.handleKeyPress(e)}
        onChange={(e) => this.setState({ textval: e.target.value })}
        disabled={!this.props.active || this.state.sending}
      />
    );

    let submit_button = (
      <Button
        className="btn btn-primary"
        style={submit_style}
        id="id_send_msg_button"
        disabled={
          this.state.textval === "" || !this.props.active || this.state.sending
        }
        onClick={() => this.tryMessageSend()}
      >
        Send
      </Button>
    );

    return (
      <div
        id="response-type-text-input"
        className="response-type-module"
        style={pane_style}
      >
        <div style={input_style}>
          {text_input}
          {submit_button}
        </div>
      </div>
    );
  }
}

function ResponsePane(props) {
  const { chatMode, taskContext, onMessageSend } = React.useContext(
    MephistoContext
  );

  let response_pane = null;
  switch (chatMode) {
    case CHAT_MODE.DONE:
    case CHAT_MODE.INACTIVE:
      response_pane = <DoneResponse />;
      break;
    case CHAT_MODE.READY_FOR_INPUT:
    case CHAT_MODE.WAITING:
      if (taskContext && taskContext["respond_with_form"]) {
        response_pane = (
          <FormResponse
            onMessageSend={onMessageSend}
            active={chatMode === CHAT_MODE.READY_FOR_INPUT}
            formOptions={taskContext["respond_with_form"]}
          />
        );
      } else {
        response_pane = (
          <TextResponse
            onMessageSend={onMessageSend}
            active={chatMode === CHAT_MODE.READY_FOR_INPUT}
          />
        );
      }
      break;
    case CHAT_MODE.IDLE:
    default:
      response_pane = <IdleResponse />;
      break;
  }

  return (
    <div
      id="right-bottom-pane"
      style={{ width: "100%", backgroundColor: "#eee" }}
    >
      {response_pane}
    </div>
  );
}

function RightPane({ children }) {
  // TODO move to CSS
  let right_pane = {
    minHeight: "100%",
    display: "flex",
    flexDirection: "column",
    justifyContent: "spaceBetween",
  };

  return (
    <div id="right-pane" style={right_pane}>
      {children}
    </div>
  );
}

function CustomTaskDescription({
  taskConfig: { chat_title, task_description },
  taskContext,
}) {
  return (
    <div>
      <h1>{chat_title}</h1>
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
          __html: task_description || "Task Description Loading",
        }}
      />
    </div>
  );
}

function LeftPane({ children, stretch = false }) {
  const { taskContext, taskConfig } = React.useContext(MephistoContext);

  let frame_height = taskConfig.frame_height;
  let frame_style = {
    height: frame_height + "px",
    backgroundColor: "#dff0d8",
    padding: "30px",
    overflow: "auto",
  };
  let pane_size = stretch ? "col-xs-12" : "col-xs-4";
  return (
    <div id="left-pane" className={pane_size} style={frame_style}>
      <CustomTaskDescription
        taskContext={taskContext}
        taskConfig={taskConfig}
      />
      {children}
    </div>
  );
}

function BaseFrontend({ messages, onMessageSend }) {
  const { connectionStatus, appSettings } = React.useContext(MephistoContext);

  if (appSettings.isCoverPage) {
    return (
      <div className="row" id="ui-content">
        <LeftPane stretch={true} />
      </div>
    );
  } else if (connectionStatus === CONNECTION_STATUS.INITIALIZING) {
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
      <div className="row" id="ui-content">
        <LeftPane />
        <RightPane>
          <ChatPane messages={messages} />
          <ResponsePane onMessageSend={onMessageSend} />
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
  TextResponse,
  ResponsePane,
  RightPane,
  LeftPane,
  BaseFrontend,
};
