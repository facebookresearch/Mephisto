/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import TasksHeader from "components/TasksHeader/TasksHeader";
import { capitalizeString, setPageTitle } from "helpers";
import * as moment from "moment/moment";
import * as React from "react";
import { useEffect } from "react";
import { Spinner, Table } from "react-bootstrap";
import { Link, useParams } from "react-router-dom";
import { getTask } from "requests/tasks";
import { getUnits } from "requests/units";
import urls from "urls";
import "./TaskUnitsPage.css";

const STATUS_COLOR_CLASS_MAPPING = {
  accepted: "text-success",
  rejected: "text-danger",
  soft_rejected: "text-warning",
};

type ParamsType = {
  id: string;
};

interface TaskUnitsPagePropsType {
  setErrors: Function;
}

function TaskUnitsPage(props: TaskUnitsPagePropsType) {
  const params = useParams<ParamsType>();

  const [task, setTask] = React.useState<TaskType>(null);
  const [units, setUnits] = React.useState<Array<UnitType>>(null);
  const [loading, setLoading] = React.useState(false);

  function onError(errorResponse: ErrorResponseType | null) {
    if (errorResponse) {
      props.setErrors((oldErrors) => [...oldErrors, ...[errorResponse.error]]);
    }
  }

  useEffect(() => {
    // Set default title
    setPageTitle("Mephisto - Task Review - Task Units");

    if (task === null) {
      getTask(params.id, setTask, setLoading, onError, null);

      getUnits(setUnits, setLoading, onError, { task_id: params.id });
    }
  }, []);

  useEffect(() => {
    if (task) {
      // Update title with current task
      setPageTitle(`Mephisto - Task Review - ${task.name} Units`);
    }
  }, [task]);

  return (
    <div className={"units"}>
      {/* Header */}
      <TasksHeader />

      {!loading && task && (
        // Task name
        <div className={"header"}>
          <div className={"task-name"}>Task: {task.name}</div>

          {units && <div>{units.length} units</div>}
        </div>
      )}

      {/* Units table */}
      <Table className={"units-table"} responsive={"sm"} bordered={false}>
        <thead>
          <tr className={"titles-row"}>
            <th className={"title worker"}>
              <b>Worker</b>
            </th>
            <th className={"title unit"}>
              <b>Unit</b>
            </th>
            <th className={"title reviewed"}>
              <b>Reviewed?</b>
            </th>
            <th className={"title status"}>
              <b>Status</b>
            </th>
            <th className={"title date"}>
              <b>Date</b>
            </th>
            <th className={"title details"}></th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {units &&
            units.map((unit: UnitType, index: number) => {
              const date = moment(unit.created_at).format("MMM D, YYYY");
              const nonClickable = !unit.is_reviewed;
              const statusColorClass = STATUS_COLOR_CLASS_MAPPING[unit.status];

              return (
                <tr className={"unit-row"} key={"unit-row" + index}>
                  <td className={"worker"}>{unit.worker_id}</td>
                  <td className={"unit"}>{unit.id}</td>
                  <td className={"reviewed"}>
                    {unit.is_reviewed ? <span>&#x2611;</span> : ""}
                  </td>
                  <td
                    className={
                      "status fw-bold" +
                      (statusColorClass ? ` ${statusColorClass}` : "")
                    }
                  >
                    {capitalizeString(unit.status.replace("_", "-"))}
                  </td>
                  <td className={"date"}>{date}</td>
                  <td className={"details"}>
                    <Link
                      to={urls.client.taskUnit(task.id, unit.id)}
                      target={"_blank"}
                    >
                      View Unit
                    </Link>
                  </td>
                  <td></td>
                </tr>
              );
            })}
        </tbody>
      </Table>

      {/* Preloader when we request units */}
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

export default TaskUnitsPage;
