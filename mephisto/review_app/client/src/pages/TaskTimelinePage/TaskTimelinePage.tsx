/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import TasksHeader from "components/TasksHeader/TasksHeader";
import { setPageTitle } from "pages/TaskPage/helpers";
import * as React from "react";
import { useEffect } from "react";
import { Spinner } from "react-bootstrap";
import { useParams } from "react-router-dom";
import { getTaskTimeline } from "requests/tasks";
import "./TaskTimelinePage.css";

type ParamsType = {
  id: string;
};

interface TaskTimelinePagePropsType {
  setErrors: Function;
}

function TaskTimelinePage(props: TaskTimelinePagePropsType) {
  const params = useParams<ParamsType>();

  const [taskTimeline, setTaskTimeline] = React.useState<TaskTimelineType>(
    null
  );
  const [loading, setLoading] = React.useState(false);

  function onError(errorResponse: ErrorResponseType | null) {
    if (errorResponse) {
      props.setErrors((oldErrors) => [...oldErrors, ...[errorResponse.error]]);
    }
  }

  // Effects
  useEffect(() => {
    // Set default title
    setPageTitle("Mephisto - Task Timeline");

    if (taskTimeline === null) {
      getTaskTimeline(params.id, setTaskTimeline, setLoading, onError, null);
    }
  }, []);

  useEffect(() => {
    if (taskTimeline) {
      if (taskTimeline.server_is_available) {
        // Redirect to Grafana dashboard
        window.location.replace(taskTimeline.dashboard_url);
      } else {
        // Update title with current task name
        setPageTitle(`Mephisto - Task Timeline - ${taskTimeline.task_name}`);
      }
    }
  }, [taskTimeline]);

  if (taskTimeline === null) {
    return null;
  }

  return (
    <div className={"task-timeline"}>
      {/* Header */}
      <TasksHeader />

      {!loading && taskTimeline && (
        // Task name
        <div className={"header"}>
          <div className={"task-name"}>Task: {taskTimeline.task_name}</div>
        </div>
      )}

      <div className={"content"}>
        {/* Preloader when we request task timeline */}
        {loading ? (
          <div className={"loading"}>
            <Spinner animation="border" role="status">
              <span className="visually-hidden">Loading...</span>
            </Spinner>
          </div>
        ) : (
          <>
            {!taskTimeline.server_is_available && (
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

export default TaskTimelinePage;
