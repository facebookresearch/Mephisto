/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import * as React from "react";
import "./Errors.css";
import ClosableErrorAlert from "../ClosableErrorAlert/ClosableErrorAlert";

interface PropsType {
  errorList: string[];
}

function Errors(props: PropsType) {
  return (
    <div className={"errors"}>
      {props.errorList.map((error: string, i: number) => {
        return (
          <ClosableErrorAlert key={"error-alert-" + i}>
            {error}
          </ClosableErrorAlert>
        );
      })}
    </div>
  );
}

export default Errors;
