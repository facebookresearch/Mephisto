/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React, { Fragment } from "react";
import CanvasDraw from "react-canvas-draw";

function LoadingScreen() {
  return <Directions>Loading...</Directions>;
}

function Directions({ children }) {
  return (
    <section className="hero is-light">
      <div className="hero-body">
        <div className="container">
          <p className="subtitle is-5">{children}</p>
        </div>
      </div>
    </section>
  );
}
function Instructions() {
  return (
    <div>
    </div>
  );
}

function TaskFrontend({ handleSubmit }) {
  return (
    <Fragment>
      <Instructions />
      <button className="button" onClick={() => handleSubmit({})}>
        Submit Task
      </button>
    </Fragment>
  );
}

export { LoadingScreen, TaskFrontend as BaseFrontend, Instructions };
