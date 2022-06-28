/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";
import { Tips, Feedback } from "mephisto-worker-addons";

function OnboardingComponent({ onSubmit }) {
  return (
    <div>
      <Directions>
        This component only renders if you have chosen to assign an onboarding
        qualification for your task. Click the button to move on to the main
        task.
      </Directions>
      <button
        className="button is-link"
        onClick={() => onSubmit({ success: true })}
      >
        Move to main task.
      </button>
    </div>
  );
}

function LoadingScreen() {
  return <Directions>Loading...</Directions>;
}

function Directions({ children }) {
  return (
    <section className="hero is-light">
      <div className="hero-body">
        <div className="container">
          <p className="subtitle is-5">{children}</p>
        </div>
      </div>
    </section>
  );
}

function SimpleFrontend({ taskData, onSubmit }) {
  return (
    <div>
      <Directions>
        Directions: Please rate the below sentence as good or bad.
      </Directions>
      <section className="section">
        <div className="container">
          <p className="subtitle is-5"></p>
          <p className="title is-3 is-spaced">{taskData.text}</p>
          <div className="field is-grouped">
            <div className="control">
              <button
                className="button is-success is-large"
                onClick={() => onSubmit({ rating: "good" })}
              >
                Mark as Good
              </button>
            </div>
            <div className="control">
              <button
                className="button is-danger is-large"
                onClick={() => onSubmit({ rating: "bad" })}
              >
                Mark as Bad
              </button>
            </div>
          </div>

          <div style={{ margin: "25rem 0 1.5rem auto", float: "right" }}>
            <Tips maxHeight="40rem" placement="top-start" />
            <span style={{ marginLeft: "1rem" }}>
              <Feedback
                maxTextLength={30}
                textAreaMinWidth="10rem"
                textAreaMaxWidth="30rem"
                questions={[
                  "This is my first question?",
                  "This is my second question?",
                  "This is a very loooooooooooooooong question",
                  "This is a very loooooooooooooooooooooooooooooooooooooooooooooooooooooooong question",
                ]}
              />
            </span>
          </div>
        </div>
      </section>
    </div>
  );
}

export { LoadingScreen, SimpleFrontend as BaseFrontend, OnboardingComponent };
