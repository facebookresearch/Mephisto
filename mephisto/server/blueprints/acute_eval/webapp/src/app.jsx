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
  TaskDescription,
  BaseFrontend,
} from "./components/core_components.jsx";
import "fetch";
import { useMephistoTask, getBlockedExplanation } from "mephisto-task";

/* ================= Application Components ================= */

function MainApp() {
  const {
    blocked_reason,
    task_config,
    is_preview,
    agent_id,
    task_data,
    handleSubmit,
  } = useMephistoTask();

  if (blocked_reason !== null) {
    return <h1>{getBlockedExplanation(blocked_reason)}</h1>;
  }
  if (task_config === null) {
    return <div>Initializing...</div>;
  }
  if (is_preview) {
    return <TaskDescription task_config={task_config} is_cover_page={true} />;
  }
  if (agent_id === null) {
    return <div>Initializing...</div>;
  }
  if (task_data === null) {
    return <h1>Gathering data...</h1>;
  }

  return (
    <div>
      <BaseFrontend
        task_data={task_data}
        task_config={task_config}
        onSubmit={handleSubmit}
      />
    </div>
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));
