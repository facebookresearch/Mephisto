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
    this.props.handleError(error, errorInfo)
    console.log("error happened in static_react_task: ", error)
    console.log("error happened in static_react_task info: ", errorInfo)
    this.setState({
      error: error,
      errorInfo: errorInfo
    })
    // You can also log error messages to an error reporting service here
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
    handleFatalError,
    blockedReason,
    blockedExplanation,
    isPreview,
    isLoading,
    initialTaskData,
    handleSubmit,
    isOnboarding,
  } = useMephistoTask();

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
