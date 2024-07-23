/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { WorkerOpinion } from "mephisto-task-addons";
import { ErrorBoundary, useMephistoTask } from "mephisto-task-multipart";
import React, { useEffect, useState } from "react";
import ReactDOM from "react-dom";
import {
  FormComposerBaseFrontend,
  LoadingScreen,
  OnboardingComponent,
} from "./components/core_components_simple.jsx";

let WITH_WORKER_OPINION = false;
try {
  WITH_WORKER_OPINION = process.env.REACT_APP__WITH_WORKER_OPINION === "true";
} catch {}

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

  const [resonseSubmitted, setResonseSubmitted] = useState(false);

  useEffect(() => {
    if (resonseSubmitted) {
      // Scroll to the bollom of the page to reveal Worker Opinion block
      window.scrollTo(0, document.body.scrollHeight);
    }
  }, [resonseSubmitted]);

  if (blockedReason !== null) {
    return (
      <div className="card bg-danger mb-4">
        <div className="card-body pt-xl-5 pb-xl-5">
          <h2 className="text-white">{blockedExplanation}</h2>
        </div>
      </div>
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
          onSubmit={(data) => {
            setResonseSubmitted(true);
            handleSubmit(data);
          }}
          onError={handleFatalError}
        />

        {WITH_WORKER_OPINION && resonseSubmitted && (
          <div className={"mx-auto mt-lg-5 mb-lg-5"} style={{ width: "600px" }}>
            <WorkerOpinion
              maxTextLength={500}
              questions={["Was this task hard?", "Is this a good example?"]}
            />
          </div>
        )}
      </ErrorBoundary>
    </div>
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));
