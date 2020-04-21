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
import $ from "jquery";
import { ParlAITask } from "mephisto-task";

function postData(url = "", data = {}) {
  // Default options are marked with *
  return fetch(url, {
    method: "POST", // *GET, POST, PUT, DELETE, etc.
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data), // body data type must match "Content-Type" header
  });
}

function postProviderRequest(endpoint, data) {
  var url = new URL(window.location.origin + endpoint);
  return postData(url, { provider_data: data }).then((res) => res.json());
}

// Sends a request to get the initial task data
function getInitTaskData(mephisto_worker_id, agent_id) {
  return postProviderRequest("/initial_task_data", {
    mephisto_worker_id: mephisto_worker_id,
    agent_id: agent_id,
  });
}

function postCompleteTask(agent_id, complete_data) {
  return postData("/submit_task", {
    USED_AGENT_ID: agent_id,
    final_data: complete_data,
  })
    .then((res) => res.json())
    .then(function (data) {
      console.log("Submitted");
    });
}

/* ================= Application Components ================= */

class StaticApp extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      task_data: null,
    };
  }

  handleIncomingTaskData(task_data) {
    console.log("Got task data", task_data);
    this.setState({ task_data: task_data });
  }

  componentDidMount() {
    getInitTaskData(
      this.props.mephisto_worker_id,
      this.props.agent_id
    ).then((packet) => this.handleIncomingTaskData(packet.data.init_data));
  }

  handleSubmit(data) {
    postCompleteTask(this.props.agent_id, data);
    handleSubmitToProvider(data);
  }

  render() {
    if (this.state.task_data === null) {
      return <h1>Loading...</h1>;
    }
    return (
      <BaseFrontend
        task_config={this.props.task_config}
        onSubmit={(data) => {
          this.handleSubmit(data);
        }}
        task_data={this.state.task_data}
      />
    );
  }
}

class WorkerBlockedView extends React.Component {
  // TODO actually have views for all block reasons
  render() {
    if (this.props.blocked_reason == "no_mobile") {
      return (
        <div>
          <h1>
            Sorry, this task cannot be completed on mobile devices. Please use a
            computer.
          </h1>
        </div>
      );
    } else if (this.props.blocked_reason == "no_websockets") {
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
    return <div> {this.props.blocked_reason} </div>;
  }
}

function MainApp() {
  return (
    <ParlAITask>
      {({
        blocked_reason,
        task_config,
        is_preview,
        agent_id,
        mephisto_worker_id,
      }) => (
        <ParlaiApp
          blocked_reason={blocked_reason}
          task_config={task_config}
          is_preview={is_preview}
          agent_id={agent_id}
          mephisto_worker_id={mephisto_worker_id}
        />
      )}
    </ParlAITask>
  );
}

function ParlaiApp({
  blocked_reason,
  task_config,
  is_preview,
  agent_id,
  mephisto_worker_id,
}) {
  if (blocked_reason !== null) {
    return (
      <WorkerBlockedView
        task_config={task_config}
        blocked_reason={blocked_reason}
      />
    );
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
