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
import {
  useMephistoTask,
  getInitTaskData,
  postCompleteTask,
} from "mephisto-task";

/* global handleSubmitToProvider */

/* ================= Application Components ================= */

function StaticApp({ task_config, mephisto_worker_id, agent_id }) {
  const [taskData, setTaskData] = React.useState(null);

  React.useEffect(() => {
    getInitTaskData(mephisto_worker_id, agent_id).then((packet) =>
      setTaskData(packet.data.init_data)
    );
  }, []);

  const handleSubmit = React.useCallback(
    (data) => {
      postCompleteTask(agent_id, data);
      handleSubmitToProvider(data);
    },
    [agent_id]
  );

  if (taskData === null) {
    return <h1>Loading...</h1>;
  }
  return (
    <BaseFrontend
      task_config={task_config}
      onSubmit={(data) => {
        handleSubmit(data);
      }}
      task_data={taskData}
    />
  );
}

function WorkerBlockedView({ blocked_reason }) {
  if (blocked_reason === "no_mobile") {
    return (
      <div>
        <h1>
          Sorry, this task cannot be completed on mobile devices. Please use a
          computer.
        </h1>
      </div>
    );
  } else if (blocked_reason === "no_websockets") {
    return (
      <div>
        <h1>
          Sorry, your browser does not support the required version of
          websockets for this task. Please upgrade to a modern browser.
        </h1>
      </div>
    );
  } else {
  }
  return <div> {blocked_reason} </div>;
}

function MainApp() {
  const {
    blocked_reason,
    task_config,
    is_preview,
    agent_id,
    mephisto_worker_id,
  } = useMephistoTask();

  if (blocked_reason !== null) {
    return <WorkerBlockedView blocked_reason={blocked_reason} />;
  } else if (is_preview) {
    if (task_config === null) {
      return <div>Loading...</div>;
    } else {
      return <TaskDescription task_config={task_config} is_cover_page={true} />;
    }
  } else if (agent_id === null) {
    return <div>Loading...</div>;
  } else {
    return (
      <div>
        <StaticApp
          task_config={task_config}
          agent_id={agent_id}
          mephisto_worker_id={mephisto_worker_id}
        />
      </div>
    );
  }
}

ReactDOM.render(<MainApp />, document.getElementById("app"));
