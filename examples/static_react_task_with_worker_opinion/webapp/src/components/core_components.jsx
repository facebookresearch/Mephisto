/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React, { useState } from "react";
import { WorkerOpinion } from "mephisto-addons";

function OnboardingComponent({ onSubmit }) {
  return (
    <div>
      <Directions>
        This component only renders if you have chosen to assign an onboarding
        qualification for your task. Click the button to move on to the main
        task.
      </Directions>

      <button
        className="btn btn-link"
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
    <div className="card mb-4" data-cy="directions-container">
      <div className="card-body container">{children}</div>
    </div>
  );
}

function SimpleFrontend({ taskData, isOnboarding, onSubmit, onError }) {
  const [resonseSubmitted, setResonseSubmitted] = useState(false);

  return (
    <div>
      <Directions>
        <h5>
          Directions:
          <br />
          Please rate the below sentence as good or bad.
          <br />
          After that leave your opinion.
        </h5>
      </Directions>

      <section className="section">
        <div className="container">
          <h2 className="mb-3" data-cy="task-data-text">
            {taskData.text}
          </h2>

          {!resonseSubmitted && (
            <div className="mb-5">
              <button
                className="btn btn-success btn-lg mr-2"
                data-cy="good-button"
                onClick={() => {
                  setResonseSubmitted(true);
                  onSubmit({ rating: "good" });
                }}
              >
                Mark as Good
              </button>

              <button
                className="btn btn-danger btn-lg ml-2"
                data-cy="bad-button"
                onClick={() => {
                  setResonseSubmitted(true);
                  onSubmit({ rating: "bad" });
                }}
              >
                Mark as Bad
              </button>
            </div>
          )}

          {resonseSubmitted && (
            <>
              <div className="mb-5">Thank you for your response!</div>

              <div style={{ width: "600px" }}>
                <WorkerOpinion
                  maxTextLength={500}
                  questions={["Was this task hard?", "Is this a good example?"]}
                />
              </div>
            </>
          )}
        </div>
      </section>
    </div>
  );
}

export { LoadingScreen, SimpleFrontend as BaseFrontend, OnboardingComponent };
