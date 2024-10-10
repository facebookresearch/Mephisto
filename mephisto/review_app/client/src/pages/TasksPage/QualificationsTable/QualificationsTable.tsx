/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { DEFAULT_DATE_FORMAT } from "consts/format";
import * as moment from "moment/moment";
import * as React from "react";
import { Button, Table } from "react-bootstrap";
import { Link } from "react-router-dom";
import urls from "urls";
import "./QualificationsTable.css";

type QualificationsTablePropsType = {
  grantedQualifications: FullGrantedQualificationType[];
  setEditModalGrantedQualification: Function;
  setEditModalShow: Function;
  setErrors: Function;
};

function QualificationsTable(props: QualificationsTablePropsType) {
  return (
    <Table
      className={`qualifications-table`}
      responsive={"sm"}
      bordered={false}
    >
      <thead>
        <tr className={`titles-row`}>
          <th className={`title qualification`}>
            <b>Qualification</b>
          </th>
          <th className={`title worker`}>
            <b>Worker</b>
          </th>
          <th className={`title value-granted`}>
            <b>Current value</b>
          </th>
          <th className={`title date-granted`}>
            <b>Updated</b>
          </th>
          <th className={`title units`}>
            <b>Units</b>
          </th>
          <th className={`title actions`}></th>
          <th></th>
        </tr>
      </thead>

      <tbody>
        {props.grantedQualifications &&
          props.grantedQualifications.map(
            (gq: FullGrantedQualificationType, index: number) => {
              const granted_at = moment(gq.granted_at).format(
                DEFAULT_DATE_FORMAT
              );

              return (
                <tr className={`value-row`} key={"qualification-row" + index}>
                  <td className={`qualification text-primary`}>
                    <Link
                      className={`qualification-link`}
                      to={urls.client.qualification(gq.qualification_id)}
                      target={"_blank"}
                      title={gq.qualification_name}
                    >
                      {gq.qualification_name}
                    </Link>
                  </td>
                  <td className={`worker`}>{gq.worker_name}</td>
                  <td className={`value-granted`}>{gq.value_current}</td>
                  <td className={`date-granted`}>{granted_at}</td>
                  <td className={`units`}>
                    {gq.units.map((unit: FGQUnit, index: number) => {
                      const unitPageUrl = urls.client.taskUnit(
                        unit.task_id,
                        unit.unit_id
                      );

                      return (
                        <React.Fragment key={`unit-task-link-${index}`}>
                          <div className={`unit`}>
                            <span className={`unit-value`}>{unit.value}</span>(
                            <Link
                              className={`task-name text-primary`}
                              to={unitPageUrl}
                              target={"_blank"}
                              title={`Task: ${unit.task_name}\nUnit: ${unit.unit_id}`}
                            >
                              {unit.task_name}
                            </Link>
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

export default QualificationsTable;
