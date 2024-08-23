/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { Popover } from "bootstrap";
import React from "react";
import { secontsToTime } from "./helpers.jsx";

const MIN_SEGMENT_WIDTH_PX = 6;

function TrackSegment({
  duration,
  isSelectedAnnotationTrack,
  onClickSegment,
  paddingLeft,
  playerSizes,
  segment,
  segmentIndex,
  segmentsColor,
  selectedSegment,
}) {
  const isSelectedSegment =
    isSelectedAnnotationTrack && selectedSegment === segmentIndex;

  let oneSecWidthPx = 0;
  if (playerSizes.progressBar?.width) {
    oneSecWidthPx = playerSizes.progressBar.width / duration;
  }
  const leftPositionPx = paddingLeft + segment.start_sec * oneSecWidthPx;
  let segmentWidthPx = (segment.end_sec - segment.start_sec) * oneSecWidthPx;
  // In case if section is too narrow, we need to make it a bit vissible
  if (segmentWidthPx < MIN_SEGMENT_WIDTH_PX) {
    segmentWidthPx = MIN_SEGMENT_WIDTH_PX;
  }

  React.useEffect(() => {
    const popovers = [
      ...document.querySelectorAll('.segment[data-toggle="popover"]'),
    ].map((el) => new Popover(el));

    return () => {
      popovers.map((p) => p.dispose());
    };
  }, [segment]);

  return (
    <div
      className={`
        segment
        ${isSelectedSegment ? "active" : ""}
      `}
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
    />
  );
}

export default TrackSegment;
