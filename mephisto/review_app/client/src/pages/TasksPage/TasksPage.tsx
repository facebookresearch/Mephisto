/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import * as moment from "moment/moment";
import * as React from "react";
import { useEffect } from "react";
import { Spinner, Table } from "react-bootstrap";
import { exportTaskResults, getTasks } from "requests/tasks";
import urls from "urls";
import TasksHeader from "./TasksHeader/TasksHeader";
import "./TasksPage.css";

const STORAGE_TASK_ID_KEY: string = "selectedTaskID";

interface PropsType {
  setErrors: Function;
}

function TasksPage(props: PropsType) {
  const { localStorage } = window;

  const [tasks, setTasks] = React.useState<Array<TaskType>>(null);
  const [loading, setLoading] = React.useState(false);
  const [taskIdExportResults, setTaskIdExportResults] = React.useState(null);
  const [loadingExportResults, setLoadingExportResults] = React.useState(false);

  const onTaskRowClick = (id: number) => {
    localStorage.setItem(STORAGE_TASK_ID_KEY, String(id));

    // Create a pseudo new link and click it to open a task in new tab (not window)
    const pseudoLink = document.createElement("a");
    pseudoLink.setAttribute("href", urls.client.task(id));
    pseudoLink.setAttribute("target", "_blank");
    pseudoLink.click();
  };

  const onError = (errorResponse: ErrorResponseType | null) => {
    if (errorResponse) {
      props.setErrors((oldErrors) => [...oldErrors, ...[errorResponse.error]]);
    }
  };

  const requestTaskResults = (taskId: number, nUnits: number) => {
    setTaskIdExportResults(taskId);

    const onSuccessExportResults = (data) => {
      setTaskIdExportResults(null);

      if (data.file_created) {
        // Create pseudo link and click it
        const linkId = "result-json";
        const link = document.createElement("a");
        link.setAttribute("style", "display: none;");
        link.id = linkId;
        link.href = urls.server.taskExportResultsJson(taskId, nUnits);
        link.target = "_blank";
        link.click();
        link.remove();
      }
    };

    exportTaskResults(
      taskId,
      onSuccessExportResults,
      setLoadingExportResults,
      onError
    );
  };

  useEffect(() => {
    document.title = "Mephisto - Task Review - All Tasks";

    if (tasks === null) {
      getTasks(setTasks, setLoading, onError, null);
    }
  }, []);

  return (
    <div className={"tasks"}>
      {/* Header */}
      <TasksHeader />

      {/* Tasks table */}
      <Table className={"tasks-table"} responsive={"sm"} bordered={false}>
        <thead>
          <tr className={"titles-row"}>
            <th className={"title task"}>
              <b>Task</b>
            </th>
            <th className={"title reviewed"}>
              <b>Reviewed?</b>
            </th>
            <th className={"title units"}>
              <b>#&nbsp;Units</b>
            </th>
            <th className={"title date"}>
              <b>Date</b>
            </th>
            <th className={"title export"}>
              <b>Export results</b>
            </th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {tasks &&
            tasks.map((task: TaskType, index) => {
              const date = moment(task.created_at).format("MMM D, YYYY");
              const nonClickable = task.is_reviewed || task.unit_count === 0;

              return (
                <tr
                  className={"task-row" + (nonClickable ? " no-hover" : "")}
                  key={"task-row" + index}
                  onClick={() => !nonClickable && onTaskRowClick(task.id)}
                >
                  <td
                    className={
                      "task" + (nonClickable ? " text-muted" : " text-primary")
                    }
                  >
                    {task.name}
                  </td>
                  <td className={"reviewed"}>
                    {task.is_reviewed ? <span>&#x2611;</span> : ""}
                  </td>
                  <td className={"units"}>{task.unit_count}</td>
                  <td className={"date"}>{date}</td>
                  <td className={"export"}>
                    {task.is_reviewed &&
                      !(
                        loadingExportResults && taskIdExportResults === task.id
                      ) && (
                        <span
                          className={"text-primary download-button"}
                          onClick={() =>
                            requestTaskResults(task.id, task.unit_count)
                          }
                        >
                          Download
                        </span>
                      )}
                    {taskIdExportResults === task.id && loadingExportResults && (
                      <div className={"export-loading"}>
                        <Spinner
                          animation="border"
                          role="status"
                          style={{ width: "1.2rem", height: "1.2rem" }}
                        >
                          <span className="visually-hidden">Loading...</span>
                        </Spinner>
                      </div>
                    )}
                  </td>
                  <td></td>
                </tr>
              );
            })}
        </tbody>
      </Table>

      {/* Preloader when we request tasks */}
      {loading && (
        <div className={"loading"}>
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
        </div>
      )}
    </div>
  );
}

export default TasksPage;
