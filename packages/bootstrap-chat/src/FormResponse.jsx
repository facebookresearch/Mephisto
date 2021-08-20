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
  Col,
  FormGroup,
  ControlLabel,
  Form,
} from "react-bootstrap";

class FormResponse extends React.Component {
  // Provide a form-like interface to MTurk interface.

  constructor(props) {
    super(props);
    // At this point it should be assumed that task_data
    // has a field "respond_with_form"
    let responses = [];
    for (let _ of this.props.formOptions) {
      responses.push("");
    }
    this.state = { responses: responses, sending: false };
  }

  tryMessageSend() {
    let form_elements = this.props.formOptions;
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
    let form_elements = this.props.formOptions;
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
              onKeyPress={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  e.stopPropagation();
                  e.nativeEvent.stopImmediatePropagation();
                }
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

export default FormResponse;
