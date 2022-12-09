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

function RemoteProcedureApp() {
  let mephistoProps = useMephistoRemoteProcedureTask({});

  let {
    blockedReason,
    blockedExplanation,
    isPreview,
    isLoading,
    handleSubmit,
    remoteProcedure,
    isOnboarding,
    handleFatalError,
  } = mephistoProps;

  const handleToxicityCalculation = remoteProcedure("determine_toxicity");

  if (isOnboarding) {
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
        <div
          className="container"
          id="ui-container"
          style={{ padding: "1rem 1.5rem" }}
        >
          <BaseFrontend
            handleSubmit={handleSubmit}
            handleToxicityCalculation={handleToxicityCalculation}
          />
        </div>
      </MephistoContext.Provider>
    </ErrorBoundary>
  );
}

ReactDOM.render(<RemoteProcedureApp />, document.getElementById("app"));
