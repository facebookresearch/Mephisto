/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";
import {
  FormControl,
  Button,
  FormGroup,
  Nav,
  NavItem,
  Col,
  ControlLabel,
  Form,
} from "react-bootstrap";
import WorkerChatPopup from "./WorkerChatPopup.jsx";
import ReviewButtons from "./ReviewButtons.jsx";

import Slider from "rc-slider";
import $ from "jquery";
import { CONNECTION_STATUS } from "mephisto-task";

import "rc-slider/assets/index.css";

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

function ChatMessage({ is_self, duration, agent_id, message }) {
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

function MessageList(props) {
  let { agent_id, messages, onClickMessage, displayNames, is_review } = props;

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
            is_self={m.id === agent_id || m.id in displayNames}
            agent_id={m.id in displayNames ? displayNames[m.id] : m.id}
            message={m.text}
            task_data={m.task_data}
            message_id={m.message_id}
            duration={is_review ? m.duration : undefined}
          />
        </div>
      ))}
    </div>
  );
}

function ConnectionIndicator({ connection_status }) {
  let indicator_style = {
    opacity: "1",
    fontSize: "11px",
    color: "white",
    float: "right",
  };
  let text = "";
  switch (connection_status) {
    case CONNECTION_STATUS.CONNECTED:
      indicator_style["background"] = "#5cb85c";
      text = "connected";
      break;
    case CONNECTION_STATUS.RECONNECTING_ROUTER:
      indicator_style["background"] = "#f0ad4e";
      text = "reconnecting to router";
      break;
    case CONNECTION_STATUS.RECONNECTING_SERVER:
      indicator_style["background"] = "#f0ad4e";
      text = "reconnecting to server";
      break;
    case CONNECTION_STATUS.DISCONNECTED_SERVER:
    case CONNECTION_STATUS.DISCONNECTED_ROUTER:
    default:
      indicator_style["background"] = "#d9534f";
      text = "disconnected";
      break;
  }

  return (
    <button
      id="connected-button"
      className="btn btn-lg"
      style={indicator_style}
      disabled={true}
    >
      {text}
    </button>
  );
}

function VolumeControl(props) {
  const { volume, onVolumeChange } = props;
  const [showSlider, setShowSlider] = React.useState(false);

  let volume_control_style = {
    opacity: "1",
    fontSize: "11px",
    color: "white",
    float: "right",
    marginRight: "10px",
  };

  let slider_style = {
    height: 26,
    width: 150,
    marginRight: 14,
    float: "left",
  };

  if (showSlider) {
    return (
      <div style={volume_control_style}>
        <div style={slider_style}>
          <Slider
            onChange={(v) => onVolumeChange(v / 100)}
            style={{ marginTop: 10 }}
            defaultValue={volume * 100}
          />
        </div>
        <Button onClick={() => setShowSlider(false)}>
          <span
            style={{ marginRight: 5 }}
            className="glyphicon glyphicon-remove"
          />
          Hide Volume
        </Button>
      </div>
    );
  } else {
    return (
      <div style={volume_control_style}>
        <Button onClick={() => setShowSlider(true)}>
          <span
            className="glyphicon glyphicon glyphicon-volume-up"
            style={{ marginRight: 5 }}
            aria-hidden="true"
          />
          Volume
        </Button>
      </div>
    );
  }
}

function ChatStatusBar(props) {
  const {
    displayWorkerChatPopup = false,
    connection_status,
    volume,
    onVolumeChange,
  } = props;

  const [chatMessages, setChatMessages] = React.useState([]);

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
      <ConnectionIndicator connection_status={connection_status} />
      <VolumeControl volume={volume} onVolumeChange={onVolumeChange} />
      {displayWorkerChatPopup && (
        <WorkerChatPopup
          off_chat_messages={chatMessages}
          onMessageSend={(msg) =>
            setChatMessages([...chatMessages, { msg, owner: 0 }])
          }
          has_new_message={2}
        />
      )}
    </div>
  );
}

function Hourglass() {
  return (
    <div
      id="hourglass"
      style={{
        marginTop: "-1px",
        marginRight: "5px",
        display: "inline",
        float: "left",
      }}
    >
      <span className="glyphicon glyphicon-hourglass" aria-hidden="true" />
    </div>
  );
}

function WaitingMessage({ agent_status }) {
  let message_style = {
    float: "left",
    display: "table",
    backgroundColor: "#fff",
  };
  let text = "Waiting for the next person to speak...";
  if (agent_status === "waiting") {
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

class ChatPane extends React.Component {
  constructor(props) {
    super(props);
    this.state = { chat_height: this.getChatHeight() };
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    if (this.props.message_count !== prevProps.message_count) {
      $("div#message-pane-segment").animate(
        {
          scrollTop: $("div#message-pane-segment").get(0).scrollHeight,
        },
        500
      );
    }
  }

  getChatHeight() {
    let entry_pane = $("div#right-bottom-pane").get(0);
    let bottom_height = 90;
    if (entry_pane !== undefined) {
      bottom_height = entry_pane.scrollHeight;
    }
    return this.props.task_config.frame_height - bottom_height;
  }

  handleResize() {
    if (this.getChatHeight() !== this.state.chat_height) {
      this.setState({ chat_height: this.getChatHeight() });
    }
  }

  render() {
    // TODO move to CSS
    let top_pane_style = {
      width: "100%",
      position: "relative",
      height: this.state.chat_height + "px",
    };

    let chat_style = {
      width: "100%",
      height: this.state.chat_height + "px",
      paddingTop: "60px",
      paddingLeft: "20px",
      paddingRight: "20px",
      paddingBottom: "20px",
      overflowY: "scroll",
    };

    window.setTimeout(() => {
      this.handleResize();
    }, 10);

    let wait_message = null;
    if (this.props.chat_state === "waiting") {
      wait_message = <WaitingMessage agent_status={this.props.agent_status} />;
    }

    return (
      <div id="right-top-pane" style={top_pane_style}>
        <ChatStatusBar {...this.props} />
        <div id="message-pane-segment" style={chat_style}>
          <MessageList {...this.props} />
          {wait_message}
        </div>
      </div>
    );
  }
}

function IdleResponse() {
  return <div id="response-type-idle" className="response-type-module" />;
}

class DoneButton extends React.Component {
  // This component is responsible for initiating the click
  // on the mturk form's submit button.

  constructor(props) {
    super(props);
    this.state = {
      feedback_shown: this.props.display_feedback,
      feedback_given: null,
    };
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    if (this.props.onInputResize !== undefined) {
      this.props.onInputResize();
    }
  }

  render() {
    let review_flow = null;
    let done_button = (
      <button
        id="done-button"
        type="button"
        className="btn btn-primary btn-lg"
        onClick={() => this.props.allDoneCallback()}
      >
        <span className="glyphicon glyphicon-ok-circle" aria-hidden="true" />{" "}
        Done with this HIT
      </button>
    );
    if (this.props.display_feedback) {
      if (this.state.feedback_shown) {
        review_flow = (
          <ReviewButtons
            {...this.props}
            onChoice={(did_give) =>
              this.setState({
                feedback_shown: false,
                feedback_given: did_give,
              })
            }
          />
        );
        done_button = null;
      } else if (this.state.feedback_given) {
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
}

class DoneResponse extends React.Component {
  componentDidUpdate(prevProps, prevState, snapshot) {
    this.props.onInputResize();
  }

  render() {
    const {
      agent_state: { done_text, task_done },
    } = this.props;

    let inactive_pane = null;
    if (done_text) {
      inactive_pane = (
        <span id="inactive" style={{ fontSize: "14pt", marginRight: "15px" }}>
          {done_text}
        </span>
      );
    }
    // TODO maybe move to CSS?
    let pane_style = {
      paddingLeft: "25px",
      paddingTop: "20px",
      paddingBottom: "20px",
      paddingRight: "25px",
      float: "left",
    };
    let done_button = <DoneButton {...this.props} />;
    if (!task_done) {
      done_button = null;
    }
    return (
      <div
        id="response-type-done"
        className="response-type-module"
        style={pane_style}
      >
        {inactive_pane}
        {done_button}
      </div>
    );
  }
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
    this.props.onInputResize();
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

class FormResponse extends React.Component {
  // Provide a form-like interface to MTurk interface.

  constructor(props) {
    super(props);
    // At this point it should be assumed that task_data
    // has a field "respond_with_form"
    let responses = [];
    for (let _ of this.props.task_data["respond_with_form"]) {
      responses.push("");
    }
    this.state = { responses: responses, sending: false };
  }

  tryMessageSend() {
    let form_elements = this.props.task_data["respond_with_form"];
    let response_data = [];
    let response_text = "";
    let all_response_filled = true;
    for (let ind in form_elements) {
      let question = form_elements[ind]["question"];
      let response = this.state.responses[ind];
      if (response === "") {
        all_response_filled = false;
      }
      response_data.push({
        question: question,
        response: response,
      });
      response_text += question + ": " + response + "\n";
    }

    if (all_response_filled && this.props.active && !this.state.sending) {
      this.setState({ sending: true });
      this.props
        .onMessageSend({
          text: response_text,
          task_data: { form_responses: response_data },
        })
        .then(() => this.setState({ sending: false }));
      // clear answers once sent
      this.setState((prevState) => {
        prevState["responses"].fill("");
        return { responses: prevState["responses"] };
      });
    }
  }

  render() {
    let form_elements = this.props.task_data["respond_with_form"];
    const listFormElements = form_elements.map((form_elem, index) => {
      let question = form_elem["question"];
      if (form_elem["type"] === "choices") {
        let choices = [<option key="empty_option" />].concat(
          form_elem["choices"].map((option_label, index) => {
            return (
              <option key={"option_" + index.toString()}>{option_label}</option>
            );
          })
        );
        return (
          <FormGroup key={"form_el_" + index}>
            <Col
              componentClass={ControlLabel}
              sm={6}
              style={{ fontSize: "16px" }}
            >
              {question}
            </Col>
            <Col sm={5}>
              <FormControl
                componentClass="select"
                style={{ fontSize: "16px" }}
                value={this.state.responses[index]}
                onChange={(e) => {
                  var text = e.target.value;
                  this.setState((prevState) => {
                    let new_res = prevState["responses"];
                    new_res[index] = text;
                    return { responses: new_res };
                  });
                }}
              >
                {choices}
              </FormControl>
            </Col>
          </FormGroup>
        );
      }
      return (
        <FormGroup key={"form_el_" + index}>
          <Col
            style={{ fontSize: "16px" }}
            componentClass={ControlLabel}
            sm={6}
          >
            {question}
          </Col>
          <Col sm={5}>
            <FormControl
              type="text"
              style={{ fontSize: "16px" }}
              value={this.state.responses[index]}
              onChange={(e) => {
                var text = e.target.value;
                this.setState((prevState) => {
                  let new_res = prevState["responses"];
                  new_res[index] = text;
                  return { responses: new_res };
                });
              }}
            />
          </Col>
        </FormGroup>
      );
    });
    let submit_button = (
      <Button
        className="btn btn-primary"
        style={{ height: "40px", width: "100px", fontSize: "16px" }}
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
        style={{
          paddingTop: "15px",
          float: "left",
          width: "100%",
          backgroundColor: "#eeeeee",
        }}
      >
        <Form
          horizontal
          style={{ backgroundColor: "#eeeeee", paddingBottom: "10px" }}
        >
          {listFormElements}
          <FormGroup>
            <Col sm={6} />
            <Col sm={5}>{submit_button}</Col>
          </FormGroup>
        </Form>
      </div>
    );
  }
}

function ResponsePane(props) {
  const { chat_state, task_data } = props;

  let response_pane = null;
  switch (chat_state) {
    case "done":
    case "inactive":
      response_pane = <DoneResponse {...this.props} />;
      break;
    case "text_input":
    case "waiting":
      if (task_data && task_data["respond_with_form"]) {
        response_pane = (
          <FormResponse {...this.props} active={chat_state === "text_input"} />
        );
      } else {
        response_pane = (
          <TextResponse {...this.props} active={chat_state === "text_input"} />
        );
      }
      break;
    case "idle":
    default:
      response_pane = <IdleResponse {...this.props} />;
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

class RightPane extends React.Component {
  handleResize() {
    if (this.chat_pane !== undefined) {
      if (this.chat_pane.handleResize !== undefined) {
        this.chat_pane.handleResize();
      }
    }
  }

  render() {
    // TODO move to CSS
    let right_pane = {
      minHeight: "100%",
      display: "flex",
      flexDirection: "column",
      justifyContent: "spaceBetween",
    };

    return (
      <div id="right-pane" style={right_pane}>
        <ChatPane
          message_count={this.props.messages.length}
          {...this.props}
          ref={(pane) => {
            this.chat_pane = pane;
          }}
        />
        <ResponsePane
          {...this.props}
          onInputResize={() => this.handleResize()}
        />
      </div>
    );
  }
}

function CustomTaskDescription({
  task_config: { chat_title, task_description },
  task_data,
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
      <p>
        The current contents of task data are as follows:{" "}
        {JSON.stringify(task_data)}
      </p>
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

function ContextView({ task_data }) {
  // TODO pull context title from templating variable
  let header_text = "Context";
  let context =
    "To render context here, write or select a ContextView " +
    "that can render your task_data, or write the desired " +
    "content into the task_data.html field of your act";
  if (task_data !== undefined && task_data.html !== undefined) {
    context = task_data.html;
  }
  return (
    <div>
      <h1>{header_text}</h1>
      <hr style={{ borderTop: "1px solid #555" }} />
      <span
        id="context"
        style={{ fontSize: "16px" }}
        dangerouslySetInnerHTML={{ __html: context }}
      />
    </div>
  );
}

function LeftPane(props) {
  const { task_config, is_cover_page, children, task_data } = this.props;

  const [state, setState] = React.useState({
    current_pane: "instruction",
    last_update: 0,
  });

  if (
    task_data.last_update !== undefined &&
    task_data.last_update > state.last_update
  ) {
    setState({
      current_pane: "context",
      last_update: task_data.last_update,
    });
  }

  let frame_height = task_config.frame_height;
  let frame_style = {
    height: frame_height + "px",
    backgroundColor: "#dff0d8",
    padding: "30px",
    overflow: "auto",
  };
  let pane_size = is_cover_page ? "col-xs-12" : "col-xs-4";
  let has_context = false; // We'll be rendering context inline
  if (is_cover_page || !has_context) {
    return (
      <div id="left-pane" className={pane_size} style={frame_style}>
        <CustomTaskDescription {...props} />
        {children}
      </div>
    );
  } else {
    // In a 2 panel layout, we need to tabulate the left pane to be able
    // to display both context and instructions
    let nav_items = [
      <NavItem
        eventKey={"instruction"}
        key={"instruction-selector"}
        title={"Task Instructions"}
      >
        {"Task Instructions"}
      </NavItem>,
      <NavItem eventKey={"context"} key={"context-selector"} title={"Context"}>
        {"Context"}
      </NavItem>,
    ];
    let display_instruction = {
      backgroundColor: "#dff0d8",
      padding: "10px 20px 20px 20px",
      flex: "1 1 auto",
    };
    let display_context = {
      backgroundColor: "#dff0d8",
      padding: "10px 20px 20px 20px",
      flex: "1 1 auto",
    };
    if (state.current_pane === "context") {
      display_instruction.display = "none";
    } else {
      display_context.display = "none";
    }
    let nav_panels = [
      <div style={display_instruction} key={"instructions-display"}>
        <CustomTaskDescription {...props} />
      </div>,
      <div style={display_context} key={"context-display"}>
        <ContextView {...props} />
      </div>,
    ];

    let frame_style = {
      height: frame_height + "px",
      backgroundColor: "#eee",
      padding: "10px 0px 0px 0px",
      overflow: "auto",
      display: "flex",
      flexFlow: "column",
    };

    return (
      <div id="left-pane" className={pane_size} style={frame_style}>
        <Nav
          bsStyle="tabs"
          activeKey={state.current_pane}
          onSelect={(key) => setState({ current_pane: key })}
        >
          {nav_items}
        </Nav>
        {nav_panels}
        {children}
      </div>
    );
  }
}

function ContentLayout(props) {
  return (
    <div className="row" id="ui-content">
      <LeftPane {...props} />
      <RightPane {...props} />
    </div>
  );
}

function BaseFrontend(props) {
  const { is_cover_page, connection_status } = props;
  let content = null;
  if (is_cover_page) {
    content = (
      <div className="row" id="ui-content">
        <LeftPane {...this.props} />
      </div>
    );
  } else if (connection_status === CONNECTION_STATUS.INITIALIZING) {
    content = <div id="ui-placeholder">Initializing...</div>;
  } else if (connection_status === CONNECTION_STATUS.WEBSOCKETS_FAILURE) {
    content = (
      <div id="ui-placeholder">
        Sorry, but we found that your browser does not support WebSockets.
        Please consider updating your browser to a newer version or using a
        different browser and check this HIT again.
      </div>
    );
  } else if (connection_status === CONNECTION_STATUS.FAILED) {
    content = (
      <div id="ui-placeholder">
        Unable to initialize. We may be having issues with our servers. Please
        refresh the page, or if that isn't working return the HIT and try again
        later if you would like to work on this task.
      </div>
    );
  } else {
    content = <ContentLayout {...props} />;
  }
  return (
    <div className="container-fluid" id="ui-container">
      {content}
    </div>
  );
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
  ContentLayout,
  BaseFrontend,
};
