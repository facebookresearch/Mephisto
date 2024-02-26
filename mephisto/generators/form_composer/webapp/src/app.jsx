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
} from "./components/core_components.jsx";
import {
  useMephistoRemoteProcedureTask,
  ErrorBoundary,
} from "mephisto-task-multipart";

/* ================= Application Components ================= */

function MainApp() {
  const {
    isLoading,
    initialTaskData,
    remoteProcedure,
    handleSubmit,
    handleFatalError,
  } = useMephistoRemoteProcedureTask();

  if (isLoading || !initialTaskData) {
    return <LoadingScreen />;
  }

  let _initialTaskData = initialTaskData;
  if (initialTaskData.hasOwnProperty("task_data")) {
    _initialTaskData = initialTaskData.task_data;
  }

  return (
    <div>
      <ErrorBoundary handleError={handleFatalError}>
        <FormComposerBaseFrontend
          taskData={_initialTaskData}
          onSubmit={handleSubmit}
          onError={handleFatalError}
          remoteProcedure={remoteProcedure}
        />
      </ErrorBoundary>
    </div>
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));
