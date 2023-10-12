/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import { Card } from "@blueprintjs/core";

function AnnotationCard({ annotation }) {
  console.log(annotation);
  const { isCorrect, trueAnnotation, currentAnnotation, imgData } = annotation;
  return (
    <div style={{ float: "left" }}>
      <p>
        <img alt={""} src={imgData} />
      </p>
      <p>Model Annotation: {currentAnnotation}</p>
      <p>Marked correct: {isCorrect ? "👍" : "👎"}</p>
      <p>Provided Annotation: {trueAnnotation}</p>
    </div>
  );
}

export default function MyDataItem({ item }) {
  const data = item.data.data;
  const annotations = data.final_submission.annotations;
  const annotation_cards = annotations.map((annotation, idx) => (
    <AnnotationCard key={"annotation-" + idx} annotation={annotation} />
  ));
  const request_count = data.requests.length / 2;
  const duration = Math.round(item.data.task_end - item.data.task_start);
  return (
    <Card style={{ overflow: "hidden" }}>
      <div style={{ display: "flex" }}>{annotation_cards}</div>
      <p>{request_count} drawings</p>
      <p>{duration} seconds</p>
    </Card>
  );
}
