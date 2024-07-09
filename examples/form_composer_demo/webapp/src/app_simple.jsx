/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import ReactDOM from "react-dom";
import {
  FormComposerBaseFrontend,
  LoadingScreen,
  OnboardingComponent,
} from "./components/core_components_simple.jsx";
import { useMephistoTask, ErrorBoundary } from "mephisto-task-multipart";

/* ================= Application Components ================= */

function MainApp() {
  const {
    blockedExplanation,
    blockedReason,
    handleFatalError,
    handleSubmit,
    initialTaskData,
    isLoading,
    isOnboarding,
  } = useMephistoTask();

  if (blockedReason !== null) {
    return (
      <section className="alert alert-danger">
        <h2 className="title is-3">{blockedExplanation}</h2>
      </section>
    );
  }

  if (isOnboarding) {
    return <OnboardingComponent onSubmit={handleSubmit} />;
  }

  if (isLoading) {
    return <LoadingScreen />;
  }

  return (
    <div>
      <ErrorBoundary handleError={handleFatalError}>
        <FormComposerBaseFrontend
          taskData={initialTaskData}
          isOnboarding={isOnboarding}
          onSubmit={handleSubmit}
          onError={handleFatalError}
        />
      </ErrorBoundary>
    </div>
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));
