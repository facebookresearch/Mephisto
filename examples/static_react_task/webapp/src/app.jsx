/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";
import ReactDOM from "react-dom";
import { BaseFrontend, LoadingScreen } from "./components/core_components.jsx";
import { useMephistoTask } from "mephisto-task";

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null, errorInfo: null };
  }

  componentDidCatch(error, errorInfo) {
    // Catch errors in any components below and re-render with error message
      this.setState({
      error: error,
      errorInfo: errorInfo
    })
    // alert Mephisto worker of a component error
    alert("error from a component" + error)
    // pass the error and errorInfo to the backend through /submit_task endpoint
    this.props.handleError({error:error.message, errorInfo:errorInfo})
  }

  render() {
    if (this.state.errorInfo) {
      // Error path
      return (
        <div>
          <h2>Something went wrong.</h2>
          <details style={{ whiteSpace: 'pre-wrap' }}>
            {this.state.error && this.state.error.toString()}
            <br />
            {this.state.errorInfo.componentStack}
          </details>
        </div>
      );
    }
    // Normally, just render children
    return this.props.children;
  }
}

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


// Adding event listener instead of using window.onerror prevents the error to be caught twice
window.addEventListener('error', function (event) {
  if (event.error.hasBeenCaught !== undefined){
    return false
  }
  event.error.hasBeenCaught = true
  if (confirm("Do you want to report the error?")) {
          console.log("You pressed OK!");
          handleFatalError({errorMsg: event.error.message, error: event.error.stack})
        } else {
          console.log("You pressed Cancel!");
        }
        return true;
})
// Test case for type 3 error
// throw new Error("test error event_handler");

  if (blockedReason !== null) {
    return (
      <section className="hero is-medium is-danger">
        <div class="hero-body">
          <h2 className="title is-3">{blockedExplanation}</h2>{" "}
        </div>
      </section>
    );
  }
  if (isLoading) {
    return <LoadingScreen />;
  }
  if (isPreview) {
    return (
      <section className="hero is-medium is-link">
        <div class="hero-body">
          <div className="title is-3">
            This is an incredibly simple React task working with Mephisto!
          </div>
          <div className="subtitle is-4">
            Inside you'll be asked to rate a given sentence as good or bad.
          </div>
        </div>
      </section>
    );
  }
  return (
    <div>
    <ErrorBoundary handleError={handleFatalError}>
      <BaseFrontend
        taskData={initialTaskData}
        onSubmit={handleSubmit}
        isOnboarding={isOnboarding}
      />
    </ErrorBoundary>
    </div>
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));
