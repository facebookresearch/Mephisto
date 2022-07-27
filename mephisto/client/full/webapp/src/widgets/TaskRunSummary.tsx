/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from "react";
import { TaskRun } from "../models";
import moment from "moment";
import cx from "classnames";

export default function TaskRunSummary({
  run,
  interactive,
}: {
  run: TaskRun;
  interactive?: boolean;
}) {
  const taskEntries = Object.entries(run.params).map(([key, value]) => (
    <span
      key={key}
      style={{ display: "inline-block", marginRight: 5, fontSize: 12 }}
    >
      <span className="param-name">{key}</span>=
      <strong className="param-value">{"" + Object.values(value)[0]}</strong>
    </span>
  ));

  return (
    <div className={cx("run-header", { interactive: interactive })}>
      <h5 className="bp3-heading" style={{ display: "inline" }}>
        {run.task_name}
      </h5>{" "}
      &mdash; {moment.utc(run.start_time).fromNow()}
      <div className="params-list" style={{ display: "block", marginTop: 10 }}>
        {taskEntries}
      </div>
      <div className="details">
        <div className="metrics highlight-first">
          <div className="metric">
            {run.task_status.created + run.task_status.launched}
            <label>Remaining</label>
          </div>
          <div className="metric">
            {run.task_status.completed +
              run.task_status.accepted +
              run.task_status.mixed +
              run.task_status.rejected}
            <label>Completed</label>
          </div>
          <div className="metric">
            {run.task_status.launched + run.task_status.assigned}
            <label>In-Flight</label>
          </div>
        </div>
      </div>
    </div>
  );
}
