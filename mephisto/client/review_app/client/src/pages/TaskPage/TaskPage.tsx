/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */


import * as React from 'react';
import { Button, Col, Container, Form, Row, Table } from 'react-bootstrap';
import './TaskPage.css';
import logo from 'static/images/logo.svg';


function TaskPage() {
  return <div className={'task'}>
    <Container className={'header'}>
      <Row>
        <Col className={"logo"} sm={3}>
          <img src={logo} alt="logo" />
        </Col>
        <Col>
          <Table className={'table'} responsive="sm" bordered={false}>
            <thead>
              <tr>
                <th></th>
                <th className={"title text-secondary"}><b>Reviewed</b></th>
                <th className={"title text-success"}><b>Approved</b></th>
                <th className={"title text-warning"}><b>Soft-Rejected</b></th>
                <th className={"title text-danger"}><b>Rejected</b></th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>worker</td>
                <td><b>15</b>/25</td>
                <td><b>16</b> (80%)</td>
                <td><b>1</b> (5%)</td>
                <td><b>3</b> (15%)</td>
              </tr>
              <tr className={"total"}>
                <td>Total</td>
                <td><b>64</b>/256</td>
                <td><b>186</b> (78%)</td>
                <td><b>23</b> (7%)</td>
                <td><b>56</b> (17%)</td>
              </tr>
            </tbody>
          </Table>
        </Col>
      </Row>
    </Container>
    <div className={"buttons"}>
      <Button variant={"success"} size="sm">Approve</Button>
      <Button variant={"warning"} size="sm">Soft-Reject</Button>
      <Button variant={"danger"} size="sm">Reject</Button>
      <Form>
        <Form.Check
            type={"checkbox"}
            label={"Apply to all N remaining items from worker"}
            id={'saveState'}
          />
      </Form>
    </div>
  </div>;
}


export default TaskPage;
