/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import { FormComposer } from "react-form-composer";

function LoadingScreen() {
  return <Directions>Loading...</Directions>;
}

function Directions({ children }) {
  return (
    <section className="text-center" data-cy="directions-container">
      <div className="alert alert-primary">
        <div className="container">
          <h2>{children}</h2>
        </div>
      </div>
    </section>
  );
}

// Required component for onboarding
function OnboardingComponent({ onSubmit }) {
  return (
    <div>
      <Directions>
        You must be younger than 18 years old to take this task.
      </Directions>

      <div className="container d-flex flex-column justify-content-center align-items-center">
        {/* Green button to confuse the user if them skipped the explanation of the task */}
        <button
          className="btn btn-success mb-2"
          onClick={() =>
            onSubmit({
              success: false, // Onboarding payload to the server
            })
          }
        >
          I'm older than 18
        </button>

        {/* Correct unswer, but with red button */}
        <button
          className="btn btn-danger"
          onClick={() =>
            onSubmit({
              success: true, // Onboarding payload to the server
            })
          }
        >
          I'm younger than 18
        </button>
      </div>
    </div>
  );
}

function ScreeningComponent({ taskData }) {
  return (
    <div className="alert alert-primary">
      Screening Unit. Please, enter "{taskData.expecting_answers.name_first}" in
      "First Name" and "{taskData.expecting_answers.email}" in "Email address
      for Mephisto"
    </div>
  );
}

function FormComposerBaseFrontend({
  taskData,
  isOnboarding,
  onSubmit,
  onError,
  finalResults = null,
}) {
  let initialConfigFormData = taskData.form;

  if (!initialConfigFormData) {
    return <div>Passed form data is invalid... Recheck your task config.</div>;
  }

  return (
    <div>
      {/* Screening banner */}
      {taskData.isScreeningUnit && <ScreeningComponent taskData={taskData} />}

      <FormComposer
        data={initialConfigFormData}
        onSubmit={onSubmit}
        finalResults={finalResults}
      />
    </div>
  );
}

export { FormComposerBaseFrontend, LoadingScreen, OnboardingComponent };
