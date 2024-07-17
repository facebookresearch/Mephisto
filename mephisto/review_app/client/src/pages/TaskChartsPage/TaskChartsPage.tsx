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
import { getTaskCharts } from "requests/tasks";
import TasksHeader from "../TasksPage/TasksHeader/TasksHeader";
import "./TaskChartsPage.css";

type ParamsType = {
  id: string;
};

interface TaskChartsPagePropsType {
  setErrors: Function;
}

function TaskChartsPage(props: TaskChartsPagePropsType) {
  const params = useParams<ParamsType>();

  const [taskCharts, setTaskCharts] = React.useState<TaskChartsType>(null);
  const [loading, setLoading] = React.useState(false);

  function onError(errorResponse: ErrorResponseType | null) {
    if (errorResponse) {
      props.setErrors((oldErrors) => [...oldErrors, ...[errorResponse.error]]);
    }
  }

  // Effects
  useEffect(() => {
    // Set default title
    setPageTitle("Mephisto - Task Charts");

    if (taskCharts === null) {
      getTaskCharts(params.id, setTaskCharts, setLoading, onError, null);
    }
  }, []);

  useEffect(() => {
    if (taskCharts) {
      if (taskCharts.server_is_available) {
        // Redirect to Grafana dashboard
        window.location.replace(taskCharts.dashboard_url);
      } else {
        // Update title with current task name
        setPageTitle(`Mephisto - Task Charts - ${taskCharts.task_name}`);
      }
    }
  }, [taskCharts]);

  if (taskCharts === null) {
    return null;
  }

  return (
    <div className={"task-charts"}>
      {/* Header */}
      <TasksHeader />

      {!loading && taskCharts && (
        // Task name
        <div className={"header"}>
          <div className={"task-name"}>Task: {taskCharts.task_name}</div>
        </div>
      )}

      <div className={"content"}>
        {/* Preloader when we request task charts */}
        {loading ? (
          <div className={"loading"}>
            <Spinner animation="border" role="status">
              <span className="visually-hidden">Loading...</span>
            </Spinner>
          </div>
        ) : (
          <>
            {!taskCharts.server_is_available && (
              <>
                <h4>Grafana server is unreachable</h4>

                <br />

                <div>
                  To see Grafana dashboard, you need:
                  <ol>
                    <li>
                      Install metrics (should have be done before running this
                      Task)
                    </li>
                    <li>Start metrics server</li>
                    <li>Refresh this page</li>
                  </ol>
                  How to install and start metrics, you can find in{" "}
                  <a
                    href={
                      "https://mephisto.ai/docs/guides/how_to_use/efficiency_organization/metrics_dashboard/"
                    }
                    target={"_blank"}
                  >
                    documentation
                  </a>
                  .
                  <br />
                  <br />
                  <button
                    className={"btn btn-primary btn-sm"}
                    onClick={() => window.location.reload()}
                  >
                    Refresh page
                  </button>
                </div>
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default TaskChartsPage;
