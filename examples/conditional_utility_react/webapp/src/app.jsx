/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";
import ReactDOM from "react-dom";
import {
  BaseFrontend,
  OnboardingComponent,
  LoadingScreen,
} from "./components/core_components.jsx";
import { useMephistoTask, ErrorBoundary } from "mephisto-task";

/* ================= Application Components ================= */

function MainApp() {
  const {
    blockedReason,
    blockedExplanation,
    isPreview,
    isLoading,
    initialTaskData,
    handleSubmit,
    handleFatalError,
    isOnboarding,
  } = useMephistoTask();

  console.log(initialTaskData);

  if (blockedReason !== null) {
    return (
      <section className="hero is-medium is-danger">
        <div class="hero-body">
          <h2 className="title is-3">{blockedExplanation}</h2>{" "}
        </div>
      </section>
    );
  }
  if (isPreview) {
    return (
      <section className="hero is-medium is-link">
        <div class="hero-body">
          <div className="title is-3">
            Utilitarianism Task Preview
          </div>
          <div className="subtitle is-4">
            In this task, you will be asked to write scenarios, and rank them based on how good or bad they are.
          </div>
        </div>
      </section>
    );
  }
  if (isLoading || !initialTaskData) {
    return <LoadingScreen />;
  }
  if (isOnboarding) {
    return <OnboardingComponent onSubmit={handleSubmit} taskData={initialTaskData}/>;
  }

  return (
    <div>
      <ErrorBoundary handleError={handleFatalError}>
      {initialTaskData.input_config !== undefined ? <BaseFrontend
          taskData={initialTaskData}
          onSubmit={handleSubmit}
          isOnboarding={isOnboarding}
          onError={handleFatalError}
        /> :null}
      </ErrorBoundary>
    </div>
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));
