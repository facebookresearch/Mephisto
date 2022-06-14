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
import { Tips } from "mephisto-worker-experience";

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
          className="container-fluid"
          id="ui-container"
          style={{ padding: "1rem 1.5rem" }}
        >
          <BaseFrontend
            handleSubmit={handleSubmit}
            handleToxicityCalculation={handleToxicityCalculation}
          />
          <Tips
            handleSubmit={(tipData) =>
              console.log(tipData.header, tipData.text)
            }
            maxHeight="25rem"
            maxWidth="25rem"
            placement="bottom-start"
            list={[
              {
                header: "Functional or Class Components?",
                text:
                  "It is generally advised to use functional components as they are thought to be the future of React.",
              },
              {
                header: "When to Use Context?",
                text:
                  "To avoid having to pass props down 3+ levels, the createContext() and useContext() methods can be used.",
              },
            ]}
          />
        </div>
      </MephistoContext.Provider>
    </ErrorBoundary>
  );
}

ReactDOM.render(<RemoteProcedureApp />, document.getElementById("app"));
