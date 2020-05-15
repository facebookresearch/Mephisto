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
} from "react-bootstrap";


class TaskDescription extends React.Component {
  render() {
    return (
      <div>
        This is an incredibly simple task to demonstrate how creating Mephisto tasks with
        react works! Inside you'll be asked to rate a given sentence as good or bad.
      </div>
    );
  }
}

class OnboardingComponent extends React.Component {
  render() {
    return (
      <div>
        <p>
          This component only renders if you have chosen to assign an onboarding qualification
          for your task. Click the button to move on to the main task.
        </p>
        <Button 
          type="button" 
          onClick={() => this.props.onSubmit({submitted: true})}
        >
          Move to main task.
        </Button>
      </div>
    )
  }
}

class SimpleFrontend extends React.Component {
  render() {
    if (!this.props.task_data) {
      return <div>Loading</div>;
    }
    if (this.props.isOnboarding) {
      return <OnboardingComponent onSubmit={(data) => this.props.onSubmit(data)} />;
    }
    let good_button = (
      <Button 
        type="button" 
        onClick={() => this.props.onSubmit({rating: "good"})}
      >
        Mark as Good
      </Button>
    )
    let bad_button = (
      <Button 
        type="button" 
        onClick={() => this.props.onSubmit({rating: "bad"})}
      >
        Mark as Bad
      </Button>
    );
    return (
      <div>
        <h1>Please rate the below sentence as good or bad</h1>
        <p>
          {this.props.task_data.text}
        </p>
        <div>
          {good_button}
          {bad_button}
        </div>
      </div>
    )
  }
}

export { TaskDescription, SimpleFrontend as BaseFrontend };
