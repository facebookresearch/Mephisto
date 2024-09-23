/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { cloneDeep } from "lodash";
import React from "react";
import AnnotationTrack from "./AnnotationTrack.jsx";
import {
  convertAnnotationTasksDataObjectsRoLists,
  convertInitialDataListsToObjects,
} from "./helpers.jsx";
import "./AnnotationTracks.css";

const INIT_ANNOTATION_TRACK = {
  title: "",
  segments: {},
};

function AnnotationTracks({
  className,
  customTriggers,
  customValidators,
  duration,
  formatStringWithTokens,
  inReviewState,
  onChange,
  onSelectSegment,
  player,
  playerSizes,
  segmentFields,
  segmentIsValid,
  segmentValidation,
  setRenderingErrors,
  setSegmentValidation,
  setVideoPlayerChapters,
  tracks,
}) {
  const [annotationTracks, setAnnotationTracks] = React.useState(
    convertInitialDataListsToObjects(tracks)
  );
  const [selectedAnnotationTrack, setSelectedAnnotationTrack] = React.useState(
    "0"
  );

  // ----- Methods -----

  function onClickAnnotationTrack(e, annotationTrack, trackIndex) {
    setSelectedAnnotationTrack(trackIndex);
    setVideoPlayerChapters(Object.values(annotationTrack.segments));
  }

  function onClickAddAnnotationTrack(e) {
    setAnnotationTracks((prevState) => {
      const newTrackIndex = Object.keys(prevState).length;
      const newTrackData = cloneDeep(INIT_ANNOTATION_TRACK);
      newTrackData.title = `Track #${newTrackIndex + 1}`;
      setSelectedAnnotationTrack(String(newTrackIndex));
      return {
        ...prevState,
        ...{ [newTrackIndex]: newTrackData },
      };
    });
  }

  // ----- Effects -----

  React.useEffect(() => {
    const resultData = convertAnnotationTasksDataObjectsRoLists(
      annotationTracks
    );
    onChange && onChange(resultData);
  }, [annotationTracks]);

  return (
    <div
      className={`
        annotation-tracks
        ${className || ""}
      `}
    >
      {!inReviewState && (
        <div className={`tracks-buttons`}>
          <button
            className={`btn btn-sm btn-primary`}
            type={"button"}
            onClick={(e) => segmentIsValid && onClickAddAnnotationTrack(e)}
            disabled={!segmentIsValid}
          >
            <i className={`las la-plus`} /> Track
          </button>
        </div>
      )}

      {Object.entries(annotationTracks).map(([trackIndex, annotationTrack]) => {
        return (
          <AnnotationTrack
            annotationTrack={annotationTrack}
            customTriggers={customTriggers}
            customValidators={customValidators}
            duration={duration}
            formatStringWithTokens={formatStringWithTokens}
            inReviewState={inReviewState}
            key={`annotation-track-${trackIndex}`}
            onClickAnnotationTrack={onClickAnnotationTrack}
            onSelectSegment={onSelectSegment}
            player={player}
            playerSizes={playerSizes}
            segmentFields={segmentFields}
            segmentIsValid={segmentIsValid}
            segmentValidation={segmentValidation}
            selectedAnnotationTrack={selectedAnnotationTrack}
            setAnnotationTracks={setAnnotationTracks}
            setRenderingErrors={setRenderingErrors}
            setSegmentValidation={setSegmentValidation}
            trackIndex={trackIndex}
          />
        );
      })}
    </div>
  );
}

export default AnnotationTracks;
