/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from 'react';
import {
  Col,
  ControlLabel,
  Form,
  FormControl,
  FormGroup,
  Grid,
  Radio,
  Row,
} from 'react-bootstrap';
import $ from 'jquery';

// blue
const speaker1_color = "#29BFFF";
// purple
const speaker2_color = "#492FED";
// grey
const otherspeaker_color = "#eee";

const speaker1_style = {
  borderRadius: 3,
  padding: "1px 4px",
  display: "inline-block",
  backgroundColor: speaker1_color,
  color: "white"
};
const speaker2_style = {
  borderRadius: 3,
  padding: "1px 4px",
  display: "inline-block",
  backgroundColor: speaker2_color,
  color: "white"
};
const otherspeaker_style = {
  borderRadius: 3,
  padding: "1px 4px",
  display: "inline-block",
  backgroundColor: otherspeaker_color
};

class ChatMessage extends React.Component {
  render() {
    let message = this.props.message;
    let primary_speaker_color = this.props.model === "model_left"
      ? speaker1_color
      : speaker2_color;
    let message_container_style = {
      display: "block",
      width: "100%",
      ...(this.props.is_primary_speaker
        ? {
            float: "left"
          }
        : {
            float: "right"
          })
    };
    let message_style = {
      borderRadius: 6,
      marginBottom: 10,
      padding: "5px 10px",
      ...(this.props.is_primary_speaker
        ? {
            marginRight: 20,
            textAlign: "left",
            float: "left",
            color: "white",
            display: "inline-block",
            backgroundColor: primary_speaker_color
          }
        : {
            textAlign: "right",
            float: "right",
            display: "inline-block",
            marginLeft: 20,
            backgroundColor: otherspeaker_color
          })
    };
    return (
      <div style={message_container_style}>
        <div style={message_style}>{message}</div>
      </div>
    );
  }
}

class MessageList extends React.Component {
  makeMessages() {
    if (this.props.task_data.pairing_dict === undefined) {
      return (
        <div>
          <p> Loading chats </p>
        </div>
      );
    }
    let task_data = this.props.task_data;
    let model = this.props.index === 0
      ? "model_left"
      : "model_right";
    let messages = task_data.task_specs[model]["dialogue"];
    let primary_speaker = task_data.task_specs[model]["name"];
    return messages.map((m, idx) => (
      <div key={model + "_" + idx}>
        <ChatMessage
          message={m.text}
          is_primary_speaker={m.id == primary_speaker}
          model={model}
        />
      </div>
    ));
  }

  render() {
    return (
      <div id="message_thread" style={{ width: "100%" }}>
        {this.makeMessages()}
      </div>
    );
  }
}

class ChatPane extends React.Component {
  constructor(props) {
    super(props);
    this.state = { chat_height: this.getChatHeight() };
  }

  getChatHeight() {
    let entry_pane = $("div#right-bottom-pane").get(0);
    let bottom_height = 90;
    if (entry_pane !== undefined) {
      bottom_height = entry_pane.scrollHeight;
    }
    return this.props.frame_height - bottom_height;
  }

  handleResize() {
    if (this.getChatHeight() != this.state.chat_height) {
      this.setState({ chat_height: this.getChatHeight() });
    }
  }

  render() {
    // TODO move to CSS
    let top_pane_style = {
      width: "100%",
      position: "relative",
      overflowY: "scroll"
    };

    let chat_style = {
      width: "100%",
      height: "100%",
      paddingTop: "60px",
      paddingLeft: "20px",
      paddingRight: "20px",
      paddingBottom: "20px",
      overflowY: "scroll"
    };

    window.setTimeout(() => {
      this.handleResize();
    }, 10);

    top_pane_style["height"] = this.state.chat_height + "px";

    return (
      <div id="right-top-pane" style={top_pane_style}>
        <Grid className="show-grid" style={{ width: "auto" }}>
          <Row>
            <Col sm={6}>
              <div id="message-pane-segment-left" style={chat_style}>
                <MessageList {...this.props} index={0} />
              </div>
            </Col>
            <Col sm={6}>
              <div id="message-pane-segment-right" style={chat_style}>
                <MessageList {...this.props} index={1} />
              </div>
            </Col>
          </Row>
        </Grid>
      </div>
    );
  }
}

class EvalResponse extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      speakerChoice: "",
      textReason: "",
      taskData: [],
      subtaskIndexSeen: 0
    };
    this.handleInputChange = this.handleInputChange.bind(this);
    this.handleEnterKey = this.handleEnterKey.bind(this);
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

  checkValidData() {
    console.log(this.state);
    if (this.state.speakerChoice !== "") {
      let response_data = {
        speakerChoice: this.state.speakerChoice,
        textReason: this.state.textReason
      };
      this.props.onValidDataChange(true, response_data);
      return;
    }
    this.props.onValidDataChange(false, {});
  }

  handleInputChange(event) {
    console.log(event);
    let target = event.target;
    let value = target.value;
    let name = target.name;

    this.setState({ [name]: value }, this.checkValidData);
  }

  handleEnterKey(event) {
    event.preventDefault();
    if (this.props.task_done) {
      this.props.allDoneCallback();
    } else if (this.props.subtask_done && this.props.show_next_task_button) {
      this.props.nextButtonCallback();
    }
  }

  render() {
    if (
      this.props.current_subtask_index != null &&
      this.props.current_subtask_index !== this.state.subtaskIndexSeen
    ) {
      this.setState({
        subtaskIndexSeen: this.props.current_subtask_index,
        textReason: "",
        speakerChoice: ""
      });
    }
    if (
      this.props.task_data === undefined ||
      this.props.task_data.task_specs === undefined
    ) {
      return <div></div>;
    }
    let s1_choice = this.props.task_data.task_specs.s1_choice.split(
      "<Speaker 1>"
    );
    let s2_choice = this.props.task_data.task_specs.s2_choice.split(
      "<Speaker 2>"
    );
    let s1_name = this.props.task_data.task_specs.model_left.name;
    let s2_name = this.props.task_data.task_specs.model_right.name;
    let form_question = this.props.task_data.task_specs.question;
    let text_question =
      "Please provide a brief justification for your choice (a few words or a sentence)";
    let text_reason = (
      <div>
        <ControlLabel>{text_question}</ControlLabel>
        <FormControl
          type="text"
          id="id_text_input"
          name="textReason"
          style={{
            width: "80%",
            height: "100%",
            float: "left",
            fontSize: "16px"
          }}
          value={this.state.textReason}
          placeholder="Please enter here..."
          onChange={this.handleInputChange}
        />
      </div>
    );
    let speaker1_div = <div style={speaker1_style}>Speaker 1</div>;
    let speaker2_div = <div style={speaker2_style}>Speaker 2</div>;
    let choice1 = (
      <div>
        {s1_choice[0]}
        {speaker1_div}
        {s1_choice[1]}
      </div>
    );
    let choice2 = (
      <div>
        {s2_choice[0]}
        {speaker2_div}
        {s2_choice[1]}
      </div>
    );
    return (
      <div
        id="response-type-text-input"
        className="response-type-module"
        style={{
          paddingTop: "15px",
          float: "left",
          width: "100%",
          backgroundColor: "#eeeeee"
        }}
      >
        <Form
          horizontal
          style={{ backgroundColor: "#eeeeee", paddingBottom: "10px" }}
          onSubmit={this.handleEnterKey}
        >
          <div className="container" style={{ width: "auto" }}>
            <ControlLabel> {form_question} </ControlLabel>
            <FormGroup>
              <Col sm={6}>
                <Radio
                  name="speakerChoice"
                  value={s1_name}
                  style={{ width: "100%" }}
                  checked={this.state.speakerChoice == s1_name}
                  onChange={this.handleInputChange}
                >
                  {choice1}
                </Radio>
              </Col>
              <Col sm={6}>
                <Radio
                  name="speakerChoice"
                  value={s2_name}
                  style={{ width: "100%" }}
                  checked={this.state.speakerChoice == s2_name}
                  onChange={this.handleInputChange}
                >
                  {choice2}
                </Radio>
              </Col>
            </FormGroup>
            {text_reason}
          </div>
        </Form>
      </div>
    );
  }
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
        <span className="glyphicon glyphicon-ok-circle" aria-hidden="true" />{' '}
        Done with this HIT
      </button>
    );
    return (
      <div>
        {review_flow}
        <div>{done_button}</div>
      </div>
    );
  }
}

class DoneResponse extends React.Component {
  render() {
    let inactive_pane = null;
    if (this.props.done_text) {
      inactive_pane = (
        <span id="inactive" style={{ fontSize: '14pt', marginRight: '15px' }}>
          {this.props.done_text}
        </span>
      );
    }
    // TODO maybe move to CSS?
    let pane_style = {
      paddingLeft: '25px',
      paddingTop: '20px',
      paddingBottom: '20px',
      paddingRight: '25px',
      float: 'left',
    };
    let done_button = <DoneButton {...this.props} />;
    if (!this.props.task_done) {
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

class TaskFeedbackPane extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      feedbackText: '',
    };
    this.handleInputChange = this.handleInputChange.bind(this);
    this.handleEnterKey = this.handleEnterKey.bind(this);
  }

  getChatHeight() {
    let entry_pane = $('div#right-bottom-pane').get(0);
    let bottom_height = 90;
    if (entry_pane !== undefined) {
      bottom_height = entry_pane.scrollHeight;
    }
    return this.props.frame_height - bottom_height;
  }

  handleResize() {
    if (this.getChatHeight() != this.state.chat_height) {
      this.setState({chat_height: this.getChatHeight()});
    }
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

  checkValidData() {
    let response_data = {
      feedbackText: this.state.feedbackText,
    }
    this.props.onValidDataChange(true, response_data);
  }

  handleInputChange(event) {
    let target = event.target;
    let value = target.value;
    let name = target.name;

    this.setState(
      {[name]: value},
      this.checkValidData
    );
  }

  handleEnterKey(event) {
    event.preventDefault();
    this.props.allDoneCallback();
  }

  render() {
    if (this.props.task_data === undefined ||
        this.props.task_data.task_specs === undefined){
      return (
        <div></div>
      );
    }
    let text_question = "If you have any feedback regarding this hit, please leave it here.\nOtherwise, click the [Done with Hit] button on the left.";
    let text_reason = (
      <div>
        <h3>(Optional)</h3>
        <h4>{text_question}</h4>
        <FormControl
          componentClass="textarea"
          id="id_text_input"
          name="feedbackText"
          style={{width: '100%', height: '100%', float: 'left', 'rows': 8, 'fontSize': '16px'}}
          value={this.state.feedbackText}
          placeholder="Please enter here..."
          onChange={this.handleInputChange}
          />
        </div>
    );
    return (
      <div
        id="response-type-text-input"
        className="response-type-module"
        style={{'paddingTop': '15px',
                'float': 'left',
                'width': '100%',
                'backgroundColor': '#ffd585'}}>
            <Form
              horizontal
              style={{backgroundColor: '#ffd585', paddingBottom: '10px'}}
              onSubmit={this.handleEnterKey}
              >
              <div
                className="container"
                style={{'width': 'auto',}}>
                {text_reason}
              </div>
            </Form>
      </div>
    );
  }
}

class ResponsePane extends React.Component {
  render() {
    let response_pane = null;
    switch (this.props.task_state) {
      case "done":
        response_pane = <DoneResponse {...this.props} />;
        break;
      default:
        response_pane = <EvalResponse {...this.props} />;
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
}

class PairwiseEvalPane extends React.Component {
  handleResize() {
    console.log("HANDLE RESIZE CALLED");
    if (this.chat_pane !== undefined && this.chat_pane !== null) {
      console.log(this.chat_pane);
      if (this.chat_pane.handleResize !== undefined) {
        console.log(this.chat_pane.handleResize);
        this.chat_pane.handleResize();
      }
    }
  }

  render() {
    let right_pane = {
      maxHeight: "60%",
      display: "flex",
      flexDirection: "column",
      justifyContent: "spaceBetween",
      width: "auto"
    };
    if (
      this.props.current_subtask_index >=
      this.props.task_description.num_subtasks
    ) {
      return (
        <div id="right-pane" style={right_pane}>
          <TaskFeedbackPane
            {...this.props}
            ref={pane => {
              this.chat_pane = pane;
            }}
            onInputResize={() => this.handleResize()}
          />
        </div>
      );
    }
    console.log("RETURNING");
    return (
      <div id="right-pane" style={right_pane}>
        <ChatPane
          {...this.props}
          message_count={this.props.messages.length}
          ref={pane => {
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

class RightPane extends React.Component {
  render() {
    // TODO move to CSS
    let right_pane = {
      minHeight: '100%',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'spaceBetween',
    };

    return (
      <div id="right-pane" style={right_pane}>
        <PairwiseEvalPane {...this.props} />
      </div>
    );
  }
}

class TaskDescription extends React.Component {
  render() {
    let header_text = "Which Conversational Partner is Better?";
    if (this.props.task_description === null) {
      return <div>Loading</div>;
    }
    let task_config = this.props.task_config
    let num_subtasks = task_config.num_subtasks;
    let question = task_config.question;
    let content = (
      <div>
        In this task, you will read two conversations and judge&nbsp;
        <div style={speaker1_style}>Speaker 1</div> on the left and&nbsp;
        <div style={speaker2_style}>Speaker 2</div> on the right&nbsp; based on
        the quality of conversation only.{" "}
        <b>Don't base your judgement&nbsp; on their hobbies, job, etc.</b>&nbsp;
        Do your best to ignore the{" "}
        <div style={otherspeaker_style}>other speaker</div>.&nbsp; You may need
        to scroll down to see the full conversations.&nbsp;
        <br />
        <br />
        You will judge <div style={speaker1_style}>Speaker 1</div> and&nbsp;
        <div style={speaker2_style}>Speaker 2</div> on this:&nbsp;
        <b>{question}</b> You should&nbsp; also provide a very brief
        justification. Failure to do so could result&nbsp; in your hits being
        rejected.
        <br />
        <br />
        <b>
          {" "}
          You will do this for {num_subtasks} pairs of conversations.&nbsp; Use
          the [NEXT] button when you're done with each judgment.
        </b>
        <br />
        <br />
        NOTE: please be sure to only accept one of this task at a time.&nbsp;
        Additional pages will show errors or fail to load and you wll not be
        able to submit the hit.&nbsp;
        <h4>Please accept the task if you're ready.</h4>
      </div>
    );
    if (!this.props.is_cover_page) {
      if (this.props.task_data.task_specs === undefined) {
        return <div>Loading</div>;
      }
      let num_subtasks = this.props.num_subtasks;
      let cur_index = this.props.current_subtask_index + 1;
      let question = this.props.task_data.task_specs.question;
      content = (
        <div>
          <b>
            You are currently at comparison {cur_index} / {num_subtasks}{" "}
          </b>
          <br />
          <br />
          You will read two conversations and judge&nbsp;
          <div style={speaker1_style}>Speaker 1</div> on the left and&nbsp;
          <div style={speaker2_style}>Speaker 2</div> on the right&nbsp; based
          on the quality of conversation.{" "}
          <b>Don't base your judgement&nbsp; on their hobbies, job, etc. </b>
          &nbsp; Do your best to ignore the{" "}
          <div style={otherspeaker_style}>other speaker</div>.&nbsp; You may
          need to scroll down to see the full conversations.&nbsp;
          <br />
          <br />
          You will judge <div style={speaker1_style}>Speaker 1</div> and&nbsp;
          <div style={speaker2_style}>Speaker 2</div> on this:&nbsp;
          <b>{question}</b> You should&nbsp; also provide a very brief
          justification. Failure to do so could result&nbsp; in your hits being
          rejected.
          <br />
          <br />
          <b>
            {" "}
            You will do this for {num_subtasks} pairs of conversations.&nbsp;
            After completing each judgement, use the [NEXT] button (which will
            appear below after you finish your judgement).
          </b>
          <br />
        </div>
      );
    }
    return (
      <div>
        <h1>{header_text}</h1>
        <hr style={{ borderTop: "1px solid #555" }} />
        {content}
      </div>
    );
  }
}

class LeftPane extends React.Component {
  render() {
    let frame_height = this.props.frame_height;
    let frame_style = {
      height: frame_height + 'px',
      backgroundColor: '#dff0d8',
      padding: '30px',
      overflow: 'auto',
    };
    let pane_size = this.props.is_cover_page ? 'col-xs-12' : 'col-xs-4';
    let has_context = this.props.task_data.has_context;
    if (this.props.is_cover_page || !has_context) {
      return (
        <div id="left-pane" className={pane_size} style={frame_style}>
          <TaskDescription {...this.props} />
          {this.props.children}
        </div>
      );
    }
  }
}

class BaseFrontend extends React.Component {
  constructor(props) {
    super(props);

    // task_description is in task_config.task_description
    // frame_height is in task_config.frame_height
    // get_task_feedback is in task_config.get_task_feedback
    // TODO move constants to props rather than state
    this.state = {
      task_done: false,
      subtask_done: false,
      task_data: {},
      all_tasks_data: this.props.task_data,
      num_subtasks: 0,
      response_data: [],
      current_subtask_index: null,
    };
  }

  onValidData(valid, response_data) {
    let all_response_data = this.state.response_data;
    let show_next_task_button = false;
    let task_done = true;
    all_response_data[this.state.current_subtask_index] = response_data;
    if ((this.state.current_subtask_index < this.state.num_subtasks - 1 ) ||
          (this.state.current_subtask_index == this.state.num_subtasks - 1 &&
            this.state.task_description.get_task_feedback)) {
      show_next_task_button = true;
      task_done = false;
    }
    this.setState(
      {
        show_next_task_button: show_next_task_button,
        subtask_done: valid,
        task_done: task_done,
        response_data: all_response_data,
      },
    );
  }

  nextButtonCallback() {
    let next_subtask_index = this.state.current_subtask_index + 1;
    if (next_subtask_index == this.state.num_subtasks) {
      this.setState(
        {
          current_subtask_index: next_subtask_index,
          task_data: Object.assign({}, this.state.task_data, {}),
          subtask_done: true,
          task_done: true,
        },
      );
    } else {
      this.setState(
        {
          current_subtask_index: next_subtask_index,
          task_data: Object.assign(
            {}, 
            this.state.task_data,
            this.state.all_tasks_data[next_subtask_index]),
          subtask_done: false,
        },
      );
    }
  }

  render() {
    let task_config = this.props.task_config;
    let all_tasks_data = this.props.task_data;
    let done_button = null;
    let passed_props = {
      onValidDataChange: (valid, data) => this.onValidData(valid, data),
      nextButtonCallback: () => this.nextButtonCallback(),
      task_config: task_config,
      next_subtask_index: this.state.next_subtask_index,
      task_data: this.state.task_data,
      task_done: this.state.task_done,
      subtask_done: this.state.subtask_done,
    };
    if (this.state.task_done) {
      done_button = <DoneResponse {...this.passed_props} />
    }
    return (
      <div className="container-fluid" id="ui-container">
        <div className="row" id="ui-content">
          <LeftPane
            {...others}
            {...passed_props}
            frame_height={frame_height}
          >
            {done_button}
          </LeftPane>
          <RightPane {...passed_props}/>
        </div>
      </div>
    );
  }
}

export {
  TaskDescription,
  BaseFrontend,
};
