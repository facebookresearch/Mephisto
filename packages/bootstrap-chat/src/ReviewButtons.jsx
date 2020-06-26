/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";

import {
  Button,
  MenuItem,
  DropdownButton,
  InputGroup,
  FormControl,
  ButtonGroup,
} from "react-bootstrap";

class ReviewButtons extends React.Component {
  GOOD_REASONS = ["Not specified", "Interesting/Creative", "Other"];

  BAD_REASONS = [
    "Not specified",
    "Didn't understand task",
    "Bad grammar/spelling",
    "Total nonsense",
    "Slow responder",
    "Other",
  ];

  RATING_VALUES = [1, 2, 3, 4, 5];

  RATING_TITLES = [
    "Terrible",
    "Bad",
    "Average/Good",
    "Great",
    "Above and Beyond",
  ];

  constructor(props) {
    super(props);
    let init_state = props.initState;
    if (init_state !== undefined) {
      this.state = init_state;
    } else {
      this.state = {
        current_rating: null,
        submitting: false,
        submitted: false,
        text: "",
        dropdown_value: "Not specified",
      };
    }
  }

  render() {
    // Create basic button selector
    let current_rating = this.state.current_rating;
    let button_vals = this.RATING_VALUES;
    let rating_titles = this.RATING_TITLES;
    let buttons = button_vals.map((v) => {
      let use_style = "info";
      if (v < 3) {
        use_style = "danger";
      } else if (v > 3) {
        use_style = "success";
      }

      return (
        <Button
          onClick={() =>
            this.setState({
              current_rating: v,
              text: "",
              dropdown_value: "Not specified",
            })
          }
          bsStyle={current_rating === v ? use_style : "default"}
          disabled={this.state.submitting}
          key={"button-rating-" + v}
        >
          {rating_titles[v - 1]}
        </Button>
      );
    });

    // Dropdown and other only appear in some cases
    let dropdown = null;
    let other_input = null;
    let reason_input = null;
    if (current_rating !== null && current_rating !== 3) {
      let options = current_rating > 3 ? this.GOOD_REASONS : this.BAD_REASONS;
      let dropdown_vals = options.map((opt) => (
        <MenuItem
          key={"dropdown-item-" + opt}
          eventKey={opt}
          onSelect={(key) => this.setState({ dropdown_value: key, text: "" })}
        >
          {opt}
        </MenuItem>
      ));
      dropdown = (
        <DropdownButton
          dropup={true}
          componentClass={InputGroup.Button}
          title={this.state.dropdown_value}
          id={"review-dropdown"}
          disabled={this.state.submitting}
        >
          {dropdown_vals}
        </DropdownButton>
      );
    }

    // Create other text
    if (dropdown !== null && this.state.dropdown_value === "Other") {
      // Optional input for if the  user says other
      other_input = (
        <FormControl
          type="text"
          placeholder="Enter reason (optional)"
          value={this.state.text}
          onChange={(t) => this.setState({ text: t.target.value })}
          disabled={this.state.submitting}
        />
      );
    }
    if (dropdown != null) {
      reason_input = (
        <div style={{ marginBottom: "8px" }}>
          Give a reason for your rating (optional):
          <InputGroup>
            {dropdown}
            {other_input}
          </InputGroup>
        </div>
      );
    }

    // Assemble flow components
    let disable_submit = this.state.submitting || current_rating == null;
    let review_flow = (
      <div>
        Rate your chat partner (fully optional & confidential):
        <br />
        <ButtonGroup>{buttons}</ButtonGroup>
        {reason_input}
        <div style={{ marginBottom: "8px" }}>
          <ButtonGroup style={{ marginBottom: "8px" }}>
            <Button
              disabled={disable_submit}
              bsStyle="info"
              onClick={() => {
                this.setState({ submitting: true });
                let feedback_data = {
                  rating: this.state.current_rating,
                  reason_category: this.state.dropdown_value,
                  reason: this.state.text,
                };
                this.props
                  .onMessageSend({
                    text: "[PEER_REVIEW]",
                    task_data: feedback_data,
                  })
                  .then(() => this.setState({ submitted: true }));
                this.props.onChoice(true);
              }}
            >
              {this.state.submitted ? "Submitted!" : "Submit Review"}
            </Button>
            <Button
              disabled={this.state.submitting}
              onClick={() => this.props.onChoice(false)}
            >
              Decline Review
            </Button>
          </ButtonGroup>
        </div>
      </div>
    );
    return review_flow;
  }
}

export default ReviewButtons;
