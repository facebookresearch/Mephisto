/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
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

  if (blockedReason !== null) {
    return (
      <div className="card bg-danger mb-4">
        <div className="card-body pt-xl-5 pb-xl-5">
          <h2 className="text-white">{blockedExplanation}</h2>
        </div>
      </div>
    );
  }

  if (isPreview) {
    return (
      <div className="card bg-primary mb-4">
        <div className="card-body pt-xl-5 pb-xl-5">
          <h2 className="text-white">
            This is an incredibly simple React task working with Mephisto!
          </h2>
          <h5 className="text-white">
            Inside you'll be asked to rate a given sentence as good or bad.
          </h5>
        </div>
      </div>
    );
  }
  if (isLoading || !initialTaskData) {
    return <LoadingScreen />;
  }
  if (isOnboarding) {
    return <OnboardingComponent onSubmit={handleSubmit} />;
  }

  return (
    <div>
      <ErrorBoundary handleError={handleFatalError}>
        <BaseFrontend
          taskData={initialTaskData}
          onSubmit={handleSubmit}
          isOnboarding={isOnboarding}
          onError={handleFatalError}
        />
      </ErrorBoundary>
    </div>
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));
