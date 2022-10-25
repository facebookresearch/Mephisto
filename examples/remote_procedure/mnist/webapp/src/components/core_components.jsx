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

function AnnotationCanvas({ onUpdate, classifyDigit, index }) {
  const [currentAnnotation, setCurrentAnnotation] = React.useState(null);
  const [trueAnnotation, setTrueAnnotation] = React.useState("");
  const [isCorrect, setIsCorrect] = React.useState(null);

  const querying = React.useRef(false);
  const changed = React.useRef(false);
  const canvasRef = React.useRef();

  function triggerUpdate() {
    onUpdate({
      isCorrect,
      trueAnnotation,
      currentAnnotation,
      imgData: canvasRef.current.getDataURL("png", false, "#FFF"),
    });
  }

  React.useEffect(() => triggerUpdate(), [isCorrect, trueAnnotation]);

  function submitAndAnnotate() {
    let urlData = canvasRef.current.getDataURL("png", false, "#FFF");
    querying.current = true;
    classifyDigit({ urlData }).then((res) => {
      setCurrentAnnotation(res["digit_prediction"]);
      triggerUpdate(urlData);
      querying.current = false;
      if (changed.current === true) {
        // If it's changed since we last ran, rerun!
        changed.current = false;
        submitAndAnnotate();
      }
    });
  }

  const canvas = (
    <CanvasDraw
      onChange={() => {
        if (!querying.current) {
          submitAndAnnotate();
        } else {
          changed.current = true; // Query once last one comes in
        }
      }}
      canvasWidth={250}
      canvasHeight={250}
      brushColor={"#000"}
      brushRadius={18}
      hideInterface={true}
      ref={(canvasDraw) => (canvasRef.current = canvasDraw)}
    />
  );

  return (
    <div
      data-cy={`canvas-container-${index}`}
      style={{ float: "left", padding: "3px", borderStyle: "solid" }}
    >
      <div data-cy={`canvas-mouse-down-container-${index}`}>{canvas}</div>
      <button
        data-cy={`clear-button-${index}`}
        className="button"
        onClick={() => canvasRef.current.eraseAll()}
      >
        {" "}
        Clear Drawing{" "}
      </button>
      <br />
      <span data-cy={`current-annotation-${index}`}>
        Current Annotation: {currentAnnotation}
      </span>
      <br />
      Annotation Correct?{" "}
      <input
        type="checkbox"
        data-cy={`correct-checkbox-${index}`}
        disabled={currentAnnotation === null}
        value={isCorrect !== true}
        onChange={() => setIsCorrect(!isCorrect)}
      />
      {!isCorrect && (
        <Fragment>
          <br />
          Corrected Annotation:
          <br />
          <input
            type="text"
            disabled={currentAnnotation === null}
            value={trueAnnotation}
            data-cy={`correct-text-input-${index}`}
            onChange={(evt) => setTrueAnnotation(evt.target.value)}
          />
        </Fragment>
      )}
    </div>
  );
}

function Instructions({ taskData }) {
  return (
    <div>
      <h1>MNIST Model Evaluator</h1>
      <p>
        {taskData?.isScreeningUnit
          ? "Screening Unit:"
          : "To submit this task, you'll need to draw 3 (single) digits in the boxes below. Our model will try to provide an annotation for each."}
      </p>
      <p>
        {taskData?.isScreeningUnit
          ? 'To submit this task you will have to correctly draw the number 3 in the box below and check the "Annotation Correct" checkbox'
          : "You can confirm or reject each of the annotations. Provide a correction if the annotation is wrong."}
      </p>
    </div>
  );
}

function TaskFrontend({ taskData, classifyDigit, handleSubmit }) {
  const NUM_ANNOTATIONS = taskData.isScreeningUnit ? 1 : 3;
  const [annotations, updateAnnotations] = React.useReducer(
    (currentAnnotation, { updateIdx, updatedAnnotation }) => {
      return currentAnnotation.map((val, idx) =>
        idx == updateIdx ? updatedAnnotation : val
      );
    },
    Array(NUM_ANNOTATIONS).fill({
      currentAnnotation: null,
      trueAnnotation: null,
      isCorrect: null,
    })
  );
  let canSubmit =
    annotations.filter((a) => a.isCorrect === true || a.trueAnnotation !== "")
      .length == NUM_ANNOTATIONS;

  return (
    <div>
      <Instructions taskData={taskData} />
      <div>
        {annotations.map((_d, idx) => (
          <AnnotationCanvas
            index={idx}
            key={"Annotation-" + String(idx)}
            classifyDigit={classifyDigit}
            onUpdate={(annotation) =>
              updateAnnotations({
                updateIdx: idx,
                updatedAnnotation: annotation,
              })
            }
          />
        ))}
        <div style={{ clear: "both" }}></div>
      </div>

      <button
        data-cy="submit-button"
        className="button"
        onClick={() =>
          handleSubmit({
            annotations: annotations,
          })
        }
        disabled={!canSubmit}
      >
        Submit Task
      </button>
    </div>
  );
}

export { LoadingScreen, TaskFrontend as BaseFrontend, Instructions };
