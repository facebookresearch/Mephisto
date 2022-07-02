/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";
import { Tips } from "mephisto-worker-addons";

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

          <div style={{ margin: "15rem 0 1.5rem auto", width: "fit-content" }}>
            <Tips maxHeight="30rem" placement="top-start" />
          </div>
        </div>
      </section>
    </div>
  );
}

export { LoadingScreen, SimpleFrontend as BaseFrontend, OnboardingComponent };
