/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import Preloader from "components/Preloader/Preloader";
import { setResponseErrors } from "helpers";
import * as React from "react";
import { useEffect } from "react";
import { getTasks } from "requests/tasks";
import TasksTable from "../TasksTable/TasksTable";
import "./TasksTab.css";

interface TasksTabPropsType {
  setErrors: Function;
}

function TasksTab(props: TasksTabPropsType) {
  const [tasks, setTasks] = React.useState<TaskType[]>(null);
  const [loading, setLoading] = React.useState(false);

  const hasTasks = tasks && tasks.length !== 0;

  const onError = (response: ErrorResponseType) =>
    setResponseErrors(props.setErrors, response);

  // Effects
  useEffect(() => {
    document.title = "Mephisto - Task Review - All Tasks";

    if (tasks === null) {
      getTasks(setTasks, setLoading, onError, null);
    }
  }, []);

  return (
    <div className={`tasks-tab`}>
      {hasTasks ? (
        <TasksTable setErrors={props.setErrors} tasks={tasks} />
      ) : (
        <div className={`empty-message`}>No available tasks yet.</div>
      )}

      <Preloader loading={loading} />
    </div>
  );
}

export default TasksTab;
