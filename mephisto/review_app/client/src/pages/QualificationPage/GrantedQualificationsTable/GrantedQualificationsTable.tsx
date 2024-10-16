/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import ColumnTitleWithSort, {
  SortArrowsState,
} from "components/ColumnTitleWithSort/ColumnTitleWithSort";
import { DEFAULT_DATE_FORMAT, DEFAULT_DATETIME_FORMAT } from "consts/format";
import { onClickSortTableColumn } from "helpers";
import * as moment from "moment/moment";
import * as React from "react";
import { Button, Table } from "react-bootstrap";
import { Link } from "react-router-dom";
import urls from "urls";
import "./GrantedQualificationsTable.css";

type CurrentSortType = {
  column: string;
  state: SortArrowsState;
};

type GrantedQualificationTablePropsType = {
  grantedQualifications: FullGrantedQualificationType[];
  onChangeSortParam: Function;
  setEditModalGrantedQualification: Function;
  setEditModalShow: Function;
  setErrors: Function;
};

function GrantedQualificationsTable(props: GrantedQualificationTablePropsType) {
  const [currentSort, setCurrentSort] = React.useState<CurrentSortType>(null);

  return (
    <Table
      className={`granted-qualification-table`}
      responsive={"sm"}
      bordered={false}
    >
      <thead>
        <tr className={`titles-row`}>
          <th className={`title worker`}>
            <b>Worker</b>
          </th>
          <th className={`title value-granted`}>
            <ColumnTitleWithSort
              onClick={(state: SortArrowsState) => {
                onClickSortTableColumn(
                  "value_current",
                  state,
                  props.onChangeSortParam,
                  setCurrentSort
                );
              }}
              state={
                currentSort?.column === "value_current"
                  ? currentSort?.state
                  : SortArrowsState.INACTIVE
              }
              title={<b>Current value</b>}
            />
          </th>
          <th className={`title date-granted`}>
            <ColumnTitleWithSort
              onClick={(state: SortArrowsState) => {
                onClickSortTableColumn(
                  "granted_at",
                  state,
                  props.onChangeSortParam,
                  setCurrentSort
                );
              }}
              state={
                currentSort?.column === "granted_at"
                  ? currentSort?.state
                  : SortArrowsState.INACTIVE
              }
              title={<b>Updated</b>}
            />
          </th>
          <th className={`title units`}>
            <b>Granted values</b>
          </th>
          <th className={`title actions`}></th>
          <th></th>
        </tr>
      </thead>

      <tbody>
        {props.grantedQualifications &&
          props.grantedQualifications.map(
            (gq: FullGrantedQualificationType, index: number) => {
              const grantedAt = moment(gq.granted_at).format(
                DEFAULT_DATE_FORMAT
              );
              const grantedAtFull = moment(gq.granted_at).format(
                DEFAULT_DATETIME_FORMAT
              );

              return (
                <tr className={`value-row`} key={"qualification-row" + index}>
                  <td className={`worker`}>{gq.worker_name}</td>
                  <td className={`value-granted`}>{gq.value_current}</td>
                  <td className={`date-granted`} title={grantedAtFull}>
                    {grantedAt}
                  </td>
                  <td className={`units`}>
                    {gq.units.map((unit: FGQUnit, index: number) => {
                      let valueAddition = "";
                      if (unit.unit_id) {
                        const unitPageUrl = urls.client.taskUnit(
                          unit.task_id,
                          unit.unit_id
                        );
                        valueAddition = unitPageUrl;
                      } else {
                        const creationDate = moment(unit.creation_date).format(
                          DEFAULT_DATE_FORMAT
                        );
                        valueAddition = creationDate;
                      }

                      const creationDateFull = moment(
                        unit.creation_date
                      ).format(DEFAULT_DATETIME_FORMAT);

                      return (
                        <React.Fragment key={`unit-task-link-${index}`}>
                          <div className={`unit`}>
                            <span className={`unit-value`}>{unit.value}</span>(
                            {unit.unit_id ? (
                              <Link
                                className={`task-name text-primary`}
                                to={valueAddition}
                                target={"_blank"}
                                title={
                                  `Task: ${unit.task_name}\n` +
                                  `Unit: ${unit.unit_id}\n` +
                                  `Time: ${creationDateFull}`
                                }
                              >
                                {unit.task_name}
                              </Link>
                            ) : (
                              <span title={creationDateFull}>
                                {valueAddition}
                              </span>
                            )}
                            )
                          </div>

                          <br />
                        </React.Fragment>
                      );
                    })}
                  </td>
                  <td className={`actions`}>
                    <Button
                      variant={"primary"}
                      size={"sm"}
                      onClick={() => {
                        props.setEditModalGrantedQualification(gq);
                        props.setEditModalShow(true);
                      }}
                    >
                      Edit
                    </Button>
                  </td>
                  <td></td>
                </tr>
              );
            }
          )}
      </tbody>
    </Table>
  );
}

export default GrantedQualificationsTable;
