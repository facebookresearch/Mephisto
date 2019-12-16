import React from "react";
import BaseWidget from "./Base";
import useAxios from "axios-hooks";
import { TaskRun, RunningTasks } from "../models";
import { task_runs__running } from "../mocks";
import { Colors, Icon } from "@blueprintjs/core";
import { createAsync, mockRequest } from "../lib/Async";
import TaskRunSummary from "./TaskRunSummary";

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
              <TaskRunSummary run={run} />
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
