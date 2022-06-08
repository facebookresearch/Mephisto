/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React, { useState } from "react";
import { Tips } from "mephisto-worker-experience";
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
    taskConfig,
    isPreview,
    isLoading,
    handleSubmit,
    remoteProcedure,
    isOnboarding,
    handleFatalError,
    handleMetadataSubmit,
  } = mephistoProps;

  const handleToxicityCalculation = remoteProcedure("determine_toxicity");
  /* const getCurrentTips = remoteProcedure("get_current_tips");
  const addTipForReview = remoteProcedure("add_tip_for_review"); */
  const [tips, setTips] = useState([]);

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
        <div>🍊</div>
        <div
          className="container"
          id="ui-container"
          style={{ padding: "1rem 1.5rem" }}
        >
          <div className="row">
            <div className="col">
              <BaseFrontend
                handleSubmit={handleSubmit}
                handleToxicityCalculation={handleToxicityCalculation}
              />
            </div>
            <div className="col">
              <button onClick={() => setTips(taskConfig["metadata"]["tips"])}>
                Show Tips
              </button>
              <Tips
                handleSubmit={(tipObj) =>
                  handleMetadataSubmit({
                    header: tipObj.header,
                    text: tipObj.body,
                    type: "tips",
                  })
                }
                list={tips}
              />
            </div>
          </div>
        </div>
      </MephistoContext.Provider>
    </ErrorBoundary>
  );
}

ReactDOM.render(<RemoteProcedureApp />, document.getElementById("app"));
