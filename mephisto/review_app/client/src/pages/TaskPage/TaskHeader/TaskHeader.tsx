/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import * as React from "react";
import { Col, Container, Row, Table } from "react-bootstrap";
import { Link } from "react-router-dom";
import logo from "static/images/logo.svg";
import urls from "urls";
import "./TaskHeader.css";

interface PropsType {
  taskStats?: TaskStatsType;
  workerId?: number;
  workerStats?: WorkerStatsType;
}

function TaskHeader(props: PropsType) {
  const wStats = props.workerStats;
  const tStats = props.taskStats;

  const toPercent = (total: number, value: number): number => {
    return total !== 0 ? Math.round((value * 100) / total) : 0;
  };

  return (
    <Container className={"task-header"}>
      <Row>
        <Col className={"logo"} sm={3}>
          <Link to={urls.client.tasks}>
            <img src={logo} alt="logo" />
          </Link>
        </Col>
        <Col />
        {wStats && tStats && (
          <Col sm={6}>
            <Table className={"table"} responsive={"sm"} bordered={false}>
              <thead>
                <tr>
                  <th></th>
                  <th className={"title center text-secondary"}>
                    <b>Reviewed</b>
                  </th>
                  <th className={"title center text-success"}>
                    <b>Approved</b>
                  </th>
                  <th className={"title center text-warning"}>
                    <b>Soft&#8209;Rejected</b>
                  </th>
                  <th className={"title center text-danger"}>
                    <b>Rejected</b>
                  </th>
                </tr>
              </thead>
              <tbody>
                {/* Worker line */}
                <tr>
                  <td>Worker&nbsp;{props.workerId}</td>
                  <td className={"center"}>
                    {wStats.total_count !== null ? (
                      <>
                        <b>{wStats.reviewed_count}</b>/{wStats.total_count}
                      </>
                    ) : (
                      <>
                        <b>--</b>/--
                      </>
                    )}
                  </td>
                  <td className={"center"}>
                    {wStats.total_count !== null ? (
                      <>
                        <b>{wStats.approved_count}</b> (
                        {toPercent(wStats.total_count, wStats.approved_count)}%)
                      </>
                    ) : (
                      <>
                        <b>--</b>
                      </>
                    )}
                  </td>
                  <td className={"center"}>
                    {wStats.total_count !== null ? (
                      <>
                        <b>{wStats.soft_rejected_count}</b> (
                        {toPercent(
                          wStats.total_count,
                          wStats.soft_rejected_count
                        )}
                        %)
                      </>
                    ) : (
                      <>
                        <b>--</b>
                      </>
                    )}
                  </td>
                  <td className={"center"}>
                    {wStats.total_count !== null ? (
                      <>
                        <b>{wStats.rejected_count}</b> (
                        {toPercent(wStats.total_count, wStats.rejected_count)}%)
                      </>
                    ) : (
                      <>
                        <b>--</b>
                      </>
                    )}
                  </td>
                </tr>

                {/* Total line */}
                <tr className={"total"}>
                  <td>Total</td>
                  <td className={"center"}>
                    {tStats.total_count !== null ? (
                      <>
                        <b>{tStats.reviewed_count}</b>/{tStats.total_count}
                      </>
                    ) : (
                      <>
                        <b>--</b>/--
                      </>
                    )}
                  </td>
                  <td className={"center"}>
                    {tStats.total_count !== null ? (
                      <>
                        <b>{tStats.approved_count}</b> (
                        {toPercent(tStats.total_count, tStats.approved_count)}%)
                      </>
                    ) : (
                      <>
                        <b>--</b>
                      </>
                    )}
                  </td>
                  <td className={"center"}>
                    {tStats.total_count !== null ? (
                      <>
                        <b>{tStats.soft_rejected_count}</b> (
                        {toPercent(
                          tStats.total_count,
                          tStats.soft_rejected_count
                        )}
                        %)
                      </>
                    ) : (
                      <>
                        <b>--</b>
                      </>
                    )}
                  </td>
                  <td className={"center"}>
                    {tStats.total_count !== null ? (
                      <>
                        <b>{tStats.rejected_count}</b> (
                        {toPercent(tStats.total_count, tStats.rejected_count)}%)
                      </>
                    ) : (
                      <>
                        <b>--</b>
                      </>
                    )}
                  </td>
                </tr>
              </tbody>
            </Table>
          </Col>
        )}
      </Row>
    </Container>
  );
}

export default TaskHeader;
