/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { setPageTitle } from "pages/TaskPage/helpers";
import * as React from "react";
import { useEffect } from "react";
import { Spinner } from "react-bootstrap";
import { useParams } from "react-router-dom";
import { getTaskStats } from "requests/tasks";
import TasksHeader from "../TasksPage/TasksHeader/TasksHeader";
import { Histogram } from "./Histogram";
import "./TaskStatsPage.css";

type ParamsType = {
  id: string;
};

interface PropsType {
  setErrors: Function;
}

function TaskStatsPage(props: PropsType) {
  const params = useParams<ParamsType>();

  const [taskStats, setTaskStats] = React.useState<TaskRusultStatsType>(null);
  const [loading, setLoading] = React.useState(false);

  const hasStats = taskStats && Object.keys(taskStats.stats).length != 0;

  function onError(errorResponse: ErrorResponseType | null) {
    if (errorResponse) {
      props.setErrors((oldErrors) => [...oldErrors, ...[errorResponse.error]]);
    }
  }

  // Effects
  useEffect(() => {
    // Set default title
    setPageTitle("Mephisto - Task Stats");

    if (taskStats === null) {
      getTaskStats(params.id, setTaskStats, setLoading, onError, null);
    }
  }, []);

  useEffect(() => {
    if (taskStats) {
      // Update title with current task name
      setPageTitle(`Mephisto - Task Stats - ${taskStats.task_name}`);
    }
  }, [taskStats]);

  if (taskStats === null) {
    return null;
  }

  return (
    <div className={"task-stats"}>
      {/* Header */}
      <TasksHeader />

      {!loading && (
        // Task name
        <div className={"header"}>
          <div className={"task-name"}>Task: {taskStats.task_name}</div>

          <div className={"task-info"}>
            <span className={"task-id"}>Task ID: {taskStats.task_id}</span>

            <span className={"workers-count"}>
              Workers count: {taskStats.workers_count}
            </span>
          </div>
        </div>
      )}

      <div className={"content"}>
        {/* Preloader when we request task stats */}
        {loading ? (
          <div className={"loading"}>
            <Spinner animation="border" role="status">
              <span className="visually-hidden">Loading...</span>
            </Spinner>
          </div>
        ) : (
          <>
            <div className={"explanation"}>
              This is response statistics to multi-choice questions.
              <br />
              It is presented in form of histograms counting amount of responses
              to each available option.
            </div>

            {/* Histograms */}
            {hasStats ? (
              <div className={"stats"}>
                {Object.entries(taskStats.stats).map(
                  ([histogramName, data]) => {
                    if (!Object.values(data).filter(Boolean).length) {
                      return;
                    }

                    const width = Object.values(data).length > 10 ? 1400 : 700;
                    const height = 300;

                    const histogramData: HistogramData[] = Object.entries(
                      data
                    ).map(([key, value]) => {
                      return {
                        label: key,
                        value: value,
                      };
                    });

                    return (
                      <div
                        className={"field-stats"}
                        key={`histogram-${histogramName}`}
                      >
                        <div className={"histogram-name"}>{histogramName}</div>

                        <Histogram
                          data={histogramData}
                          width={width}
                          height={height}
                        />
                      </div>
                    );
                  }
                )}
              </div>
            ) : (
              <div>This task has no statistics yet.</div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default TaskStatsPage;
