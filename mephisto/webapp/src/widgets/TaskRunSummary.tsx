import React from "react";
import { TaskRun } from "../models";
import { Tag, Intent, Colors } from "@blueprintjs/core";
import moment from "moment";

export default function TaskRunSummary({ run }: { run: TaskRun }) {
  return (
    <div
      className="run-header"
      style={{
        backgroundColor: Colors.LIGHT_GRAY5,
        padding: 10,
        marginBottom: "10px",
        borderColor: Colors.GRAY5,
        borderWidth: 1,
        borderStyle: "solid",
        borderRadius: 5
      }}
    >
      <h5 className="bp3-heading" style={{ display: "inline" }}>
        {run.task_name}
      </h5>{" "}
      &mdash; {moment.utc(run.start_time).fromNow()}
      {/* <Tag
        icon="play"
        intent={Intent.SUCCESS}
        interactive={false}
        style={{ float: "right", marginLeft: 10 }}
      >
        Running
      </Tag> */}
      <code
        className="bp3-code params-list"
        style={{ display: "block", marginTop: 10 }}
      >
        {run.param_string}
      </code>
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
