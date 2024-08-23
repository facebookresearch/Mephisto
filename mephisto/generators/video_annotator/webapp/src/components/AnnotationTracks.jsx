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

const INIT_ANNOTATION_TRACK = {
  title: "",
  segments: {},
};

function AnnotationTracks({
  className,
  duration,
  inReviewState,
  onChange,
  onSelectSegment,
  player,
  playerSizes,
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
      newTrackData.title = `#${newTrackIndex + 1}`;
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
            onClick={(e) => onClickAddAnnotationTrack(e)}
          >
            <i className={`las la-plus`} /> Track
          </button>
        </div>
      )}

      {Object.entries(annotationTracks).map(([trackIndex, annotationTrack]) => {
        return (
          <AnnotationTrack
            annotationTrack={annotationTrack}
            duration={duration}
            inReviewState={inReviewState}
            key={`annotation-track-${trackIndex}`}
            onClickAnnotationTrack={onClickAnnotationTrack}
            onSelectSegment={onSelectSegment}
            player={player}
            playerSizes={playerSizes}
            selectedAnnotationTrack={selectedAnnotationTrack}
            setAnnotationTracks={setAnnotationTracks}
            trackIndex={trackIndex}
          />
        );
      })}
    </div>
  );
}

export default AnnotationTracks;
