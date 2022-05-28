/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React, { Fragment, useState } from "react";
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
      <h1>Toxicity Detection Model</h1>
      <p>
        To submit this task, you'll need to enter a sentence of sentences in the
        input box below. The model will calculate the toxicity of the inputted
        text.
      </p>
    </div>
  );
}

function TaskFrontend({ handleSubmit, handleToxicityCalculation }) {
  const [text, setText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState("");
  const [toxicity, setToxicity] = useState("0");

  function calculateToxicity() {
    setIsLoading(true);
    handleToxicityCalculation({
      text: text,
    }).then((response) => {
      setIsLoading(false);
      setToxicity(response.toxicity);
      setResult(
        `The statement, "${text}," has a toxicity of: ${response.toxicity}`
      );
    });
  }

  return (
    <Fragment>
      <Instructions />
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          width: "min(90%, 20rem)",
        }}
      >
        <textarea
          placeholder="type your text here"
          onChange={(e) => setText(e.target.value)}
          style={{ margin: "0.5rem 0 1rem" }}
          disabled={isLoading}
        />
        <button
          style={{ marginBottom: "0.5rem" }}
          className="button"
          disabled={isLoading || text.length === 0}
          onClick={calculateToxicity}
        >
          {isLoading ? <span className="loader"></span> : "Calculate Toxicity"}
        </button>
        <div style={{ marginBottom: "0.5rem" }}>{result}</div>
        <button
          className="button"
          disabled={isLoading}
          onClick={() => handleSubmit({ toxicity: toxicity })}
        >
          Submit Task
        </button>
      </div>
    </Fragment>
  );
}

export { LoadingScreen, TaskFrontend as BaseFrontend, Instructions };
