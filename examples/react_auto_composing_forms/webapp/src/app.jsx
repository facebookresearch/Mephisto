/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import ReactDOM from "react-dom";
import { AutoComposingFormFrontend, LoadingScreen } from "./components/core_components.jsx";
import { useMephistoTask, ErrorBoundary } from "mephisto-task";

/* ================= Application Components ================= */

function MainApp() {
  const {
    isLoading,
    initialTaskData,
    handleSubmit,
    handleFatalError,
  } = useMephistoTask();

  if (isLoading || !initialTaskData) {
    return <LoadingScreen />;
  }

  return (
    <div>
      <ErrorBoundary handleError={handleFatalError}>
        <AutoComposingFormFrontend
          taskData={initialTaskData}
          onSubmit={handleSubmit}
          onError={handleFatalError}
        />
      </ErrorBoundary>
    </div>
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));
