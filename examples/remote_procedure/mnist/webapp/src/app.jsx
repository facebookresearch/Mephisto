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
  LoadingScreen,
  Instructions,
} from "./components/core_components.jsx";

import {
  MephistoContext,
  useMephistoRemoteProcedureTask,
  ErrorBoundary,
} from "mephisto-task";

/* ================= Application Components ================= */

// Generate a random id
function uuidv4() {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
    var r = (Math.random() * 16) | 0,
      v = c == "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

function RemoteProcedureApp() {
  let mephistoProps = useMephistoRemoteProcedureTask({});

  let {
    blockedReason,
    blockedExplanation,
    taskConfig,
    isPreview,
    previewHtml,
    isLoading,
    handleSubmit,
    remoteProcedure,
    isOnboarding,
    handleFatalError,
    initialTaskData,
  } = mephistoProps;

  const classifyDigit = remoteProcedure("classify_digit");

  if (isOnboarding) {
    // TODO You can use this as an opportunity to display anything you want for
    // an onboarding agent

    // At the moment, this task has no onboarding
    return <h1>This task doesn't currently have an onboarding example set</h1>;
  }
  if (blockedReason !== null) {
    return <h1>{blockedExplanation}</h1>;
  }
  if (isLoading) {
    return <LoadingScreen />;
  }
  if (isPreview) {
    return <Instructions />;
  }
  return (
    <ErrorBoundary handleError={handleFatalError}>
      <MephistoContext.Provider value={mephistoProps}>
        <div className="container-fluid" id="ui-container">
          <BaseFrontend
            classifyDigit={classifyDigit}
            handleSubmit={handleSubmit}
            taskData={initialTaskData["task_data"]}
          />
        </div>
      </MephistoContext.Provider>
    </ErrorBoundary>
  );
}

function TaskPreviewView({ description }) {
  return (
    <div className="preview-screen">
      <div
        dangerouslySetInnerHTML={{
          __html: description,
        }}
      />
    </div>
  );
}

ReactDOM.render(<RemoteProcedureApp />, document.getElementById("app"));
