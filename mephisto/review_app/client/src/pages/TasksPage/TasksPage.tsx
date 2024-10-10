/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import Tabs from "components/Tabs/Tabs";
import TasksHeader from "components/TasksHeader/TasksHeader";
import * as React from "react";
import QualificationsTab from "./QualificationsTab/QualificationsTab";
import "./TasksPage.css";
import TasksTab from "./TasksTab/TasksTab";

type TasksPagePropsType = {
  setErrors: Function;
};

function TasksPage(props: TasksPagePropsType) {
  const tabs: TabType[] = [
    {
      name: "tasks",
      title: "Tasks",
      children: <TasksTab setErrors={props.setErrors} />,
      noMargins: true,
    },
    {
      name: "worker_qualifications",
      title: "Worker Qualifications",
      children: <QualificationsTab setErrors={props.setErrors} />,
      noMargins: true,
    },
  ];

  return (
    <div className={"tasks"}>
      <TasksHeader />

      <Tabs tabs={tabs} />
    </div>
  );
}

export default TasksPage;
