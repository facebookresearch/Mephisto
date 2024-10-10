/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { DEFAULT_DATE_FORMAT } from "consts/format";
import { setResponseErrors } from "helpers";
import * as moment from "moment/moment";
import * as React from "react";
import { Spinner, Table } from "react-bootstrap";
import { Link } from "react-router-dom";
import { exportTaskResults } from "requests/tasks";
import urls from "urls";
import "./TasksTable.css";

const STORAGE_TASK_ID_KEY: string = "selectedTaskID";
const ENABLE_INCOMPLETE_TASK_RESULTS_EXPORT = true;

interface TasksTablePropsType {
  setErrors: Function;
  tasks: TaskType[];
}

function TasksTable(props: TasksTablePropsType) {
  const { localStorage } = window;

  const [taskIdExportResults, setTaskIdExportResults] = React.useState(null);
  const [loadingExportResults, setLoadingExportResults] = React.useState(false);

  const onError = (response: ErrorResponseType) =>
    setResponseErrors(props.setErrors, response);

  function onTaskRowClick(id: string) {
    localStorage.setItem(STORAGE_TASK_ID_KEY, String(id));

    // Create a pseudo new link and click it to open a task in new tab (not window)
    const pseudoLink = document.createElement("a");
    pseudoLink.setAttribute("href", urls.client.task(id));
    pseudoLink.setAttribute("target", "_blank");
    pseudoLink.click();
  }

  function requestTaskResults(
    e: React.MouseEvent<HTMLElement>,
    taskId: string,
    nUnits: number
  ) {
    e.stopPropagation();

    setTaskIdExportResults(taskId);

    function onSuccessExportResults(data) {
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
    }

    exportTaskResults(
      taskId,
      onSuccessExportResults,
      setLoadingExportResults,
      onError
    );
  }

  return (
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
          <th className={"title stats"}>
            <b>Stats</b>
          </th>
          <th className={"title timeline"}>
            <b>Timeline</b>
          </th>
          <th className={"title worker-opinions"}>
            <b>Opinions</b>
          </th>
          <th className={"title display-units"}>
            <b>View Units</b>
          </th>
          <th className={"title export"}>
            <b>Export results</b>
          </th>
          <th></th>
        </tr>
      </thead>

      <tbody>
        {props.tasks &&
          props.tasks.map((task: TaskType, index: number) => {
            const date = moment(task.created_at).format(DEFAULT_DATE_FORMAT);
            const nonClickable = task.is_reviewed || task.unit_all_count === 0;
            const allowTaskResultsDownload =
              ENABLE_INCOMPLETE_TASK_RESULTS_EXPORT || task.is_reviewed;

            return (
              <tr
                className={"value-row" + (nonClickable ? " no-hover" : "")}
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
                <td className={"units"}>
                  {task.unit_finished_count}/{task.unit_all_count}
                </td>
                <td className={"date"}>{date}</td>
                <td className={"stats"}>
                  {task.has_stats && (
                    <Link to={urls.client.taskStats(task.id)} target={"_blank"}>
                      Show
                    </Link>
                  )}
                </td>
                <td className={"timeline"}>
                  <Link
                    to={urls.client.taskTimeline(task.id)}
                    target={"_blank"}
                  >
                    Show
                  </Link>
                </td>
                <td className={"worker-opinions"}>
                  <Link
                    to={urls.client.taskWorkerOpinions(task.id)}
                    target={"_blank"}
                  >
                    Show
                  </Link>
                </td>
                <td className={"display-units"}>
                  <Link to={urls.client.taskUnits(task.id)} target={"_blank"}>
                    Show
                  </Link>
                </td>
                <td className={"export"}>
                  {allowTaskResultsDownload &&
                    !(
                      loadingExportResults && taskIdExportResults === task.id
                    ) && (
                      <span
                        className={"text-primary download-button"}
                        onClick={(e: React.MouseEvent<HTMLElement>) =>
                          requestTaskResults(
                            e,
                            task.id,
                            task.unit_completed_count
                          )
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
  );
}

export default TasksTable;
