/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import * as moment from 'moment/moment';
import * as React from 'react';
import { useEffect } from 'react';
import { Spinner, Table } from 'react-bootstrap';
import { getTasks } from 'requests/tasks';
import urls from 'urls';
import TasksHeader from './TasksHeader/TasksHeader';
import './TasksPage.css';


const STORAGE_TASK_ID_KEY: string = 'selectedTaskID';


function TasksPage() {
  const { localStorage } = window;

  const [tasks, setTasks] = React.useState<Array<TaskType>>(null);
  const [loading, setLoading] = React.useState(false);
  const [errors, setErrors] = React.useState<ErrorResponseType>(null);

  const onTaskRowClick = (id: number) => {
    localStorage.setItem(STORAGE_TASK_ID_KEY, String(id));

    // Create a pseudo new link and click it to open a task in new tab (not window)
    const pseudoLink = document.createElement("a");
    pseudoLink.setAttribute("href", urls.client.task(id));
    pseudoLink.setAttribute("target", "_blank");
    pseudoLink.click();
  }

  useEffect(() => {
    document.title = "Mephisto - Task Review - All Tasks";

    if (tasks === null) {
      getTasks(setTasks, setLoading, setErrors, null);
    }
  }, []);

  return <div className={"tasks"}>
    {/* Header */}
    <TasksHeader />

    {/* Request errors */}
    {errors && (
      <div>Request errors: {errors.error}</div>
    )}

    {/* Tasks table */}
    <Table className={"tasks-table"} responsive={"sm"} bordered={false}>
      <thead>
        <tr className={"titles-row"}>
          <th className={"title task"}><b>Task</b></th>
          <th className={"title reviewed"}><b>Reviewed?</b></th>
          <th className={"title units"}><b>#&nbsp;Units</b></th>
          <th className={"title date"}><b>Date</b></th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {tasks && tasks.map((task: TaskType, index) => {
          const date = moment(task.created_at).format("MMM D, YYYY");

          return <tr
            className={"task-row" + (task.is_reviewed ? " no-hover" : "")}
            key={"task-row" + index}
            onClick={() => !task.is_reviewed && onTaskRowClick(task.id)}
          >
            <td className={"task" + (task.is_reviewed ? " text-muted" : " text-primary")}>
              {task.name}
            </td>
            <td className={"reviewed"}>{task.is_reviewed ? <span>&#x2611;</span> : ""}</td>
            <td className={"units"}>{task.unit_count}</td>
            <td className={"date"}>{date}</td>
            <td></td>
          </tr>;
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
  </div>;
}


export default TasksPage;
