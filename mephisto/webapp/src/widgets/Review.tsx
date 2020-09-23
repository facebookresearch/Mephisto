/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from "react";
import BaseWidget from "./Base";
import useAxios from "axios-hooks";
import { createAsync, mockRequest } from "../lib/Async";
import { Icon, Colors, Button, Intent } from "@blueprintjs/core";
import { ReviewableTasks } from "../models";
import TaskRunSummary from "./TaskRunSummary";
import { Link } from "react-router-dom";

const Async = createAsync<ReviewableTasks>();

export default (function ReviewWidget() {
  const reviewAsync = useAxios({
    url: "task_runs/reviewable",
  });

  return (
    <BaseWidget badge="Step 3" heading={<span>Review it</span>}>
      <Async
        info={reviewAsync}
        onLoading={() => (
          <div className="bp3-skeleton">
            <div className="bp3-non-ideal-state">
              <div
                className="bp3-non-ideal-state-visual"
                style={{ fontSize: 20 }}
              >
                <span className="bp3-icon bp3-icon-inbox-search"></span>
              </div>
              <div>You have no work to review.</div>
            </div>
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
        onData={({ data }) => (
          <span>
            {data.task_runs.map((run) => (
              <Link
                key={run.task_run_id}
                to={"/review/" + run.task_run_id}
                style={{ textDecoration: "none", color: "inherit" }}
              >
                <TaskRunSummary
                  key={run.task_run_id}
                  run={run}
                  interactive={true}
                />
              </Link>
            ))}
          </span>
        )}
        checkIfEmptyFn={(data) => data.task_runs}
        onEmptyData={() => (
          <div>
            <div className="bp3-non-ideal-state">
              <div
                className="bp3-non-ideal-state-visual"
                style={{ fontSize: 20 }}
              >
                <span className="bp3-icon bp3-icon-inbox-search"></span>
              </div>
              <div>You have no work to review.</div>
            </div>
          </div>
        )}
      />
    </BaseWidget>
  );
} as React.FC);
