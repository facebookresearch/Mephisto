/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";
function LoadingScreen() {
  return <Directions>Loading...</Directions>;
}

function Directions({ children }) {
  return (
    <section className="hero is-light">
      <div className="hero-body">
        <div className="container">
          <p className="subtitle is-5">{children}</p>
        </div>
      </div>
    </section>
  );
}

function TaskFrontend({ taskData, handleRemoteCall, handleSubmit }) {
  if (!taskData) {
    return <LoadingScreen />;
  }

  const [queryCount, setQueryCount] = React.useState(0);
  let canSubmit = queryCount > 3;

  return (
    <div>
      <h1 data-cy="directions-header">
        This is a simple task to demonstrate a static task with backend
        capabilities.
      </h1>
      <p data-cy="directions-paragraph">
        To submit this task, you must make a few backend queries first
      </p>

      <button
        data-cy="query-backend-button"
        className="button"
        onClick={() => {
          setQueryCount(queryCount + 1);
          handleRemoteCall({
            arg1: "hello",
            arg2: "goodbye",
            arg3: queryCount,
          }).then((response) => alert(JSON.stringify(response)));
        }}
      >
        Query Backend
      </button>
      <button
        data-cy="submit-button"
        className="button"
        onClick={() =>
          handleSubmit({
            backendActionsDone: queryCount,
          })
        }
        disabled={!canSubmit}
      >
        Submit Task
      </button>
    </div>
  );
}

export { LoadingScreen, TaskFrontend as BaseFrontend };
