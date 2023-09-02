/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import * as React from 'react';
import { useEffect } from 'react';
import { Button } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { getTasks } from 'requests/tasks';
import urls from 'urls';
import css from './TasksPage.css';


const STORAGE_TASK_ID_KEY: string = 'selectedTaskID';


function TasksPage() {
  const navigate = useNavigate();
  const { localStorage } = window;

  const [tasks, setTasks] = React.useState<Array<Task>>(null);
  const [loading, setLoading] = React.useState(false);
  const [errors, setErrors] = React.useState<ErrorResponse>(null);

  const onTaskClick = (id: number) => {
    localStorage.setItem(STORAGE_TASK_ID_KEY, String(id));
    navigate(urls.client.task(id));
  }

  useEffect(() => {
    if (tasks === null) {
      getTasks(setTasks, setLoading, setErrors, null);
    }
  }, []);

  return <div className={css.tasks}>
    Tasks:

    {errors && (
      <div>{errors.error}</div>
    )}

    {tasks && tasks.map((task: Task, index) => {
      return <div key={'task' + index}>
        <Button
          variant={task.is_reviewed ? "secondary" : "primary"}
          size="sm"
          title={task.created_at}
          onClick={() => !task.is_reviewed && onTaskClick(task.id)}
          disabled={task.is_reviewed}
        >
          Name "{task.name}". Units: {task.unit_count} {task.is_reviewed ? ". Reviewed" : ""}
        </Button>
      </div>;
    })}
  </div>;
}


export default TasksPage;
