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
    <section className="hero" data-cy="directions">
      <p>{children}</p>
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
        <h1 className="task-text" data-cy="task-text">
          {taskData.text}
        </h1>
        <div className="button-row">
          <button
            data-cy="good-button"
            className="button good"
            onClick={() => onSubmit({ rating: "good" })}
          >
            Mark as Good
          </button>
          <button
            data-cy="bad-button"
            className="button bad"
            onClick={() => onSubmit({ rating: "bad" })}
          >
            Mark as Bad
          </button>
        </div>
        <div style={{ margin: "10rem 0 0 0", width: "min(25rem, 100%)" }}>
          <Tips
            width="25rem"
            maxHeight="30rem"
            placement="top-start"
            maxHeaderLength={30}
            maxTextLength={300}
          />
          <div style={{ margin: "1rem 0 0" }}>
            <Feedback
              maxTextLength={30}
              questions={[
                "What is your favorite part of this task?",
                "Were you satisfied with this task?",
              ]}
            />
          </div>
        </div>
      </section>
    </div>
  );
}

export { LoadingScreen, SimpleFrontend as BaseFrontend, OnboardingComponent };
