/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React, { useState } from "react";
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
    previewHtml,
    isLoading,
    handleSubmit,
    remoteProcedure,
    isOnboarding,
    handleFatalError,
    agentId,
    assignmentId,
    handleTipSubmit,
  } = mephistoProps;

  const handleToxicityCalculation = remoteProcedure("determine_toxicity");
  /* const getCurrentTips = remoteProcedure("get_current_tips");
  const addTipForReview = remoteProcedure("add_tip_for_review"); */
  const [tips, setTips] = useState([]);
  const [tipText, setTipText] = useState("")
  console.log("agentId: ", agentId);
  console.log("assignmentId: ", assignmentId);

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

  const tipsComponents = tips.map((tipText, index) => {
    return <div key={`tip-${index}`}>{tipText}</div>;
  });

  return (
    <ErrorBoundary handleError={handleFatalError}>
      <MephistoContext.Provider value={mephistoProps}>
        <div>testing</div>
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
              {/* <button
                onClick={() =>
                  getCurrentTips({})
                    .then((response) => {
                      console.log(response);
                      setTips(response.currentTips);
                    })
                    .catch((err) => console.error(err))
                }
              >
                Show Tips!
              </button> */}
              {tipsComponents}
              <input onBlur={(e)=> setTipText(e.target.value)}/>
              <button
                disabled={tipText.length === 0}
                onClick={() =>
                  /* addTipForReview({
                    tipText: "submitted tip, wow!",
                    agentId: agentId,
                  }) */
                  handleTipSubmit({ tipText: tipText })
                }
              >
                Add tip
              </button>
            </div>
          </div>
        </div>
      </MephistoContext.Provider>
    </ErrorBoundary>
  );
}

ReactDOM.render(<RemoteProcedureApp />, document.getElementById("app"));
