/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import * as React from "react";
import { Col, Container, Row, Table } from "react-bootstrap";
import { Link } from "react-router-dom";
import logo from "static/images/logo.svg";
import urls from "urls";
import "./TaskHeader.css";

interface TaskHeaderPropsType {
  loading: boolean;
  taskStats?: TaskStatsType;
  workerId?: number;
  workerStats?: WorkerStatsType;
}

interface StatCountWithPercentagePropsType {
  count: number;
  totalCount: number;
}

function StatCountWithPercentage(props: StatCountWithPercentagePropsType) {
  const { totalCount, count } = props;

  function toPercent(total: number, value: number): number {
    return total !== 0 ? Math.round((value * 100) / total) : 0;
  }

  return totalCount !== null ? (
    <>
      <b>{count}</b>{" "}
      <span className={"percentage"}>({toPercent(totalCount, count)}%)</span>
    </>
  ) : (
    <>
      <b>--</b>
    </>
  );
}

function TaskHeader(props: TaskHeaderPropsType) {
  const wStats = props.workerStats;
  const tStats = props.taskStats;

  return (
    <Container className={"task-header"}>
      <Row>
        <Col className={"logo"} sm={3}>
          {!props.loading ? (
            <Link to={urls.client.tasks} title={"Go to Tasks list"}>
              <img src={logo} alt="logo" />
            </Link>
          ) : (
            <img src={logo} alt="logo" />
          )}
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
                    <StatCountWithPercentage
                      totalCount={wStats.total_count}
                      count={wStats.approved_count}
                    />
                  </td>
                  <td className={"center"}>
                    <StatCountWithPercentage
                      totalCount={wStats.total_count}
                      count={wStats.soft_rejected_count}
                    />
                  </td>
                  <td className={"center"}>
                    <StatCountWithPercentage
                      totalCount={wStats.total_count}
                      count={wStats.rejected_count}
                    />
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
                    <StatCountWithPercentage
                      totalCount={tStats.total_count}
                      count={tStats.approved_count}
                    />
                  </td>
                  <td className={"center"}>
                    <StatCountWithPercentage
                      totalCount={tStats.total_count}
                      count={tStats.soft_rejected_count}
                    />
                  </td>
                  <td className={"center"}>
                    <StatCountWithPercentage
                      totalCount={tStats.total_count}
                      count={tStats.rejected_count}
                    />
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
