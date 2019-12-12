import React from "react";
import BaseWidget from "./Base";
import useAxios from "axios-hooks";
import cx from "classnames";
import { TaskRun, RunningTasks } from "../models";
import { task_runs__running } from "../mocks";
import { Card, Colors, Tag, Intent, Icon } from "@blueprintjs/core";
import moment from "moment";
import { createAsync, ResponseValues, mockRequest } from "../lib/Async";

const Async = createAsync<RunningTasks>();

export default (function LaunchWidget() {
  // const runningTasksAsync = useAxios<RunningTasks>({
  //   url: "task_runs/running"
  // });

  const runningTasksAsync = mockRequest<RunningTasks>(task_runs__running);

  return (
    <BaseWidget badge="Step 2" heading={<span>Launch it</span>}>
      <Async
        info={runningTasksAsync}
        onLoading={() => (
          <div className="bp3-non-ideal-state bp3-skeleton">
            <div
              className="bp3-non-ideal-state-visual"
              style={{ fontSize: 20 }}
            >
              <span className="bp3-icon bp3-icon-clean"></span>
            </div>
            <div>You have no tasks running.</div>
          </div>
        )}
        onData={({ data }) => (
          <div>
            {data.task_runs.map((run: TaskRun) => (
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
            ))}
          </div>
        )}
        checkIfEmptyFn={data => data.task_runs}
        onEmptyData={() => (
          <div className="bp3-non-ideal-state">
            <div
              className="bp3-non-ideal-state-visual"
              style={{ fontSize: 20 }}
            >
              <span className="bp3-icon bp3-icon-clean"></span>
            </div>
            <div>You have no tasks running.</div>
          </div>
        )}
        onError={({ refetch }) => (
          <span>
            <Icon icon="warning-sign" color={Colors.RED3} /> Something went
            wrong.{" "}
            <a onClick={() => refetch()}>
              <strong>Try again</strong>
            </a>
          </span>
        )}
      />
      <div>
        <div style={{ textAlign: "center", marginTop: 15 }}>
          <button className="bp3-button" disabled>
            [TODO] Launch a task
          </button>
        </div>
      </div>
    </BaseWidget>
  );
} as React.FC);
