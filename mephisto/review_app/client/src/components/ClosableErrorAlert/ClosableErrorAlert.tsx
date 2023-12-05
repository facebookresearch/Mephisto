/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import * as React from "react";
import { useState } from "react";
import { Alert } from "react-bootstrap";
import "./ClosableErrorAlert.css";

interface PropsType {
  children: any;
}

function ClosableErrorAlert(props: PropsType) {
  const [show, setShow] = useState<boolean>(true);

  if (show) {
    return (
      <Alert
        className={"error-alert"}
        variant={"danger"}
        onClose={() => setShow(false)}
        dismissible
      >
        <Alert.Heading as={"h5"}>You got an error!</Alert.Heading>
        <div className={"alert-content"}>{props.children}</div>
      </Alert>
    );
  }
}

export default ClosableErrorAlert;
