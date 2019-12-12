import React from "react";
import BaseWidget from "./Base";
import useAxios from "axios-hooks";
import cx from "classnames";
import { RunningTasks } from "../models";
import { task_runs__running } from "../mocks";
import { Card, Colors, Tag, Intent } from "@blueprintjs/core";
import moment from "moment";

export default (function LaunchWidget() {
  // const [{ data, loading, error }, refetch] = useAxios<RunningTasks>({
  //   url: "task_runs/running"
  //   // delayed: true
  // });

  let loading, error;
  const data = task_runs__running;

  return (
    <BaseWidget badge="Step 2" heading={<span>Launch it</span>}>
      <div className={cx({ "bp3-skeleton": loading })}>
        {error ? (
          <div>An error occured</div>
        ) : loading || data.task_runs.length === 0 ? (
          <div className="bp3-non-ideal-state">
            <div
              className="bp3-non-ideal-state-visual"
              style={{ fontSize: 20 }}
            >
              <span className="bp3-icon bp3-icon-clean"></span>
            </div>
            <div>You have no tasks running.</div>
            <button className="bp3-button ">[TODO] Launch a task</button>
          </div>
        ) : (
          <div>
            {data.task_runs.map(run => (
              <div
                className="run-header"
                style={{
                  backgroundColor: Colors.LIGHT_GRAY4,
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
                &mdash; {moment(run.start_time).fromNow()}
                <Tag
                  icon="play"
                  intent={Intent.SUCCESS}
                  interactive={false}
                  style={{ float: "right", marginLeft: 10 }}
                >
                  Running
                </Tag>
                <code
                  className="bp3-code"
                  style={{ display: "block", marginTop: 10 }}
                >
                  {run.param_string}
                </code>
              </div>
            ))}
          </div>
        )}
        <div style={{ textAlign: "center", marginTop: 15 }}>
          <button className="bp3-button ">[TODO] Launch a task</button>
        </div>
      </div>
    </BaseWidget>
  );
} as React.FC);
