/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import * as React from "react";
import { Col, Container, Row } from "react-bootstrap";
import { Link } from "react-router-dom";
import logo from "static/images/logo.svg";
import urls from "urls";
import "./TasksHeader.css";

interface PropsType {}

function TasksHeader(props: PropsType) {
  return (
    <Container className={"tasks-header"}>
      <Row>
        <Col className={"logo"} sm={3}>
          <Link to={urls.client.home}>
            <img src={logo} alt="logo" />
          </Link>
        </Col>
        <Col />
      </Row>
    </Container>
  );
}

export default TasksHeader;
