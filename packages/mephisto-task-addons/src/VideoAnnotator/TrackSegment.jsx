/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { Popover } from "bootstrap";
import React from "react";
import { MIN_SEGMENT_WIDTH_PX } from "./constants";
import { secontsToTime } from "./helpers.jsx";
import "./TrackSegment.css";

function TrackSegment({
  duration,
  isSelectedAnnotationTrack,
  onClickSegment,
  paddingLeft,
  playerSizes,
  segment,
  segmentIndex,
  segmentIsValid,
  segmentsColor,
  selectedSegment,
}) {
  const isSelectedSegment =
    isSelectedAnnotationTrack &&
    String(selectedSegment) === String(segmentIndex);

  let oneSecWidthPx = 0;
  if (playerSizes.progressBar?.width) {
    oneSecWidthPx = playerSizes.progressBar.width / duration;
  }
  const leftPositionPx = paddingLeft + segment.start_sec * oneSecWidthPx;
  let segmentWidthPx = (segment.end_sec - segment.start_sec) * oneSecWidthPx;
  // In case if segment is too narrow, we need to make it a bit vissible
  if (segmentWidthPx < MIN_SEGMENT_WIDTH_PX) {
    segmentWidthPx = MIN_SEGMENT_WIDTH_PX;
  }

  const segmentId = `id-segment-${segmentIndex}`;

  React.useEffect(() => {
    const popovers = [
      ...document.querySelectorAll(`#${segmentId}[data-toggle="popover"]`),
    ].map((el) => new Popover(el));

    return () => {
      popovers.map((p) => p.dispose());
    };
  }, []);

  return (
    <div
      className={`
        segment
        ${isSelectedSegment ? "active" : ""}
        ${!segmentIsValid ? "non-clickable" : ""}
      `}
      id={segmentId}
      style={{
        width: `${segmentWidthPx}px`,
        left: `${leftPositionPx}px`,
        backgroundColor: `var(--${segmentsColor}-color)`,
      }}
      onClick={(e) => onClickSegment(e, segmentIndex)}
      data-html={true}
      data-placement={"top"}
      data-content={`
        <span>
          Time: <b>${secontsToTime(segment.start_sec)} - ${secontsToTime(
        segment.end_sec
      )}</b>
        </span>
      `}
      data-title={segment.title}
      data-toggle={"popover"}
      data-trigger={"hover"}
      // HACK to pass values into event listeners as them cannot read updated React states
      data-startsec={segment.start_sec}
      data-endsec={segment.end_sec}
    />
  );
}

export default TrackSegment;
