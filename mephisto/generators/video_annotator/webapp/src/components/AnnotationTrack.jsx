/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { cloneDeep } from "lodash";
import React from "react";
import { secontsToTime } from "./helpers.jsx";
import TrackSegment from "./TrackSegment.jsx";

// When we click on segment, we simulate clicking on track as well, and it must be first,
// but setting states is async
const DELAY_CLICK_ON_SECTION_MSEC = 200;

const START_NEXT_SECTION_PLUS_SEC = 0;

const COLORS = ["blue", "green", "orange", "purple", "red", "yellow", "brown"];

const INIT_SECTION = {
  description: "",
  end_sec: 0,
  start_sec: 0,
  title: "",
};

function AnnotationTrack({
  annotationTrack,
  duration,
  inReviewState,
  onClickAnnotationTrack,
  onSelectSegment,
  player,
  playerSizes,
  selectedAnnotationTrack,
  setAnnotationTracks,
  trackIndex,
}) {
  const [trackTitle, setTrackTitle] = React.useState(annotationTrack.title);

  const [inEditState, setInEditState] = React.useState(false);
  const [selectedSegment, setSelectedSegment] = React.useState(null);
  const [segmentToChange, setSegmentToChange] = React.useState(null);

  const isSelectedAnnotationTrack = selectedAnnotationTrack === trackIndex;

  const showSegmentToChangeInfo =
    selectedAnnotationTrack === trackIndex && segmentToChange !== null;

  // Calculate paddings to the segments to make position of segments
  // exactly under VideoPlayer progress bar
  let paddingLeft = 0;
  let paddingRight = 0;
  if (playerSizes.progressBar?.left && playerSizes.player?.left) {
    paddingLeft = playerSizes.progressBar.left - playerSizes.player.left;
    paddingRight = playerSizes.player.right - playerSizes.progressBar.right;
  }
  const segmentsColorIndex =
    trackIndex - Math.floor(trackIndex / COLORS.length) * COLORS.length;
  const segmentsColor = COLORS[segmentsColorIndex];

  const showSegments = !!Object.keys(annotationTrack.segments).length;

  // ----- Methods -----

  function onClickTrack(e) {
    onClickAnnotationTrack(e, annotationTrack, trackIndex);
  }

  function onClickEditTrackInfo(e) {
    setInEditState(true);
  }

  function onClickSaveTrackInfo(e) {
    setInEditState(false);
    setAnnotationTracks((prevState) => {
      const newState = cloneDeep(prevState);
      newState[trackIndex].title = trackTitle;
      return newState;
    });
  }

  function onClickCancelChangesTrackInfo(e) {
    setInEditState(false);
    setTrackTitle(annotationTrack.title);
  }

  function onClickRemoveTrack(e) {
    if (window.confirm("Do you really want to delete this track?")) {
      setAnnotationTracks((prevState) => {
        const newState = cloneDeep(prevState);
        delete newState[trackIndex];
        return newState;
      });

      setInEditState(false);
    }
  }

  function onClickRemoveSegment(e) {
    if (window.confirm("Do you really want to delete this segment?")) {
      setAnnotationTracks((prevState) => {
        const newState = cloneDeep(prevState);
        if (selectedSegment !== null) {
          delete newState[trackIndex].segments[selectedSegment];
        }
        return newState;
      });

      setInEditState(false);
      setSelectedSegment(null);
      setSegmentToChange(null);
    }
  }

  function onClickAddSegment(e) {
    const segmentsCount = Object.keys(annotationTrack.segments).length;

    const newSegment = cloneDeep(INIT_SECTION);
    newSegment.title = `#${segmentsCount + 1} Segment`;

    if (segmentsCount !== 0) {
      const latestSegment = annotationTrack.segments[segmentsCount - 1];
      newSegment.start_sec =
        latestSegment.end_sec + START_NEXT_SECTION_PLUS_SEC;
      newSegment.end_sec = newSegment.start_sec;
    }

    const newSegmentIndex = segmentsCount;

    setAnnotationTracks((prevState) => {
      const prevAnnotationTrack = cloneDeep(prevState[trackIndex]);
      prevAnnotationTrack.segments[newSegmentIndex] = newSegment;
      return {
        ...prevState,
        ...{ [trackIndex]: prevAnnotationTrack },
      };
    });
  }

  function validateTimeFieldsOnSave() {
    const errors = [];

    // If start is greater than end
    if (segmentToChange.start_sec > segmentToChange.end_sec) {
      errors.push(`Start of the section cannot be greater than end of it.`);
    }

    // If segment is inside another segment
    Object.entries(annotationTrack.segments).map(([segmentIndex, segment]) => {
      // Skip currently saving segment
      if (String(segmentIndex) === String(selectedSegment)) {
        return;
      }

      if (
        segmentToChange.start_sec > segment.start_sec &&
        segmentToChange.start_sec < segment.end_sec
      ) {
        errors.push(
          `You cannot start a segment in already created segment before: ` +
            `${segment.title} ${secontsToTime(
              segment.start_sec
            )} - ${secontsToTime(segment.end_sec)}`
        );
      }

      if (
        segmentToChange.end_sec > segment.start_sec &&
        segmentToChange.end_sec < segment.end_sec
      ) {
        errors.push(
          `You cannot end a segment in already created segment before: ` +
            `${segment.title} ${secontsToTime(
              segment.start_sec
            )} - ${secontsToTime(segment.end_sec)}`
        );
      }
    });

    return errors;
  }

  function onClickSaveSegmentData(e) {
    const errors = validateTimeFieldsOnSave();

    if (errors.length) {
      // Show alert with errors
      const errorMessage =
        `You cannot save this segment, according to the following errors:\n\n` +
        `${errors.join("\n")}\n\n` +
        `Fix errors and try again.\n\n` +
        `Note that, if you need to create segments in parallel, create a new track and continue work there.`;
      window.alert(errorMessage);
    } else {
      // Save  a segment
      setAnnotationTracks((prevState) => {
        const prevAnnotationTrack = cloneDeep(prevState[trackIndex]);
        prevAnnotationTrack.segments[selectedSegment] = segmentToChange;
        return {
          ...prevState,
          ...{ [trackIndex]: prevAnnotationTrack },
        };
      });
    }
  }

  function onClickRestoreOldSegmentData(e) {
    const oldSegmentData = annotationTrack.segments[selectedSegment];
    setSegmentToChange(oldSegmentData);
  }

  function onClickSegment(e, segmentIndex) {
    player.pause();
    setTimeout(
      () => setSelectedSegment(segmentIndex),
      DELAY_CLICK_ON_SECTION_MSEC
    );
  }

  function onClickSaveFormField(e, fieldName, value) {
    setSegmentToChange((prevState) => {
      return {
        ...prevState,
        ...{ [fieldName]: value },
      };
    });
  }

  // ----- Effects -----

  React.useEffect(() => {
    // Deselect all selected segments when we select new annotation track
    setSelectedSegment(null);
    setSegmentToChange(null);

    if (selectedAnnotationTrack !== trackIndex) {
      setInEditState(false);
    }
  }, [selectedAnnotationTrack]);

  React.useEffect(() => {
    if (selectedSegment !== null) {
      const _segmentToChange = annotationTrack.segments[selectedSegment];
      setSegmentToChange(_segmentToChange);
      onSelectSegment && onSelectSegment(_segmentToChange);
    }
  }, [selectedSegment]);

  return (
    <div
      className={`
        annotation-track
        ${isSelectedAnnotationTrack ? "active" : ""}
      `}
      onClick={(e) => onClickTrack()}
    >
      {/* Short name on unactive track */}
      {!isSelectedAnnotationTrack && (
        <div className={`track-name-small`}>{annotationTrack.title}</div>
      )}

      {isSelectedAnnotationTrack && (
        <div className={`track-info`}>
          <span className={`track-name-label`}>Track:</span>

          {inEditState ? (
            <input
              className={`form-control form-control-sm`}
              name={"track-name"}
              value={trackTitle}
              onChange={(e) => setTrackTitle(e.target.value)}
            />
          ) : (
            <span className={`track-name`}>{annotationTrack.title}</span>
          )}

          {!inReviewState && (
            <>
              <div className={`buttons`}>
                {inEditState ? (
                  <>
                    <button
                      className={`btn btn-sm btn-success`}
                      type={"button"}
                      onClick={(e) => onClickSaveTrackInfo(e)}
                    >
                      <i className={`las la-save`} />
                    </button>

                    <button
                      className={`btn btn-sm btn-outline-danger`}
                      type={"button"}
                      onClick={(e) => onClickCancelChangesTrackInfo(e)}
                    >
                      <i className={`las la-times`} />
                    </button>
                  </>
                ) : (
                  <>
                    <button
                      className={`btn btn-sm btn-outline-dark`}
                      type={"button"}
                      onClick={(e) => onClickEditTrackInfo(e)}
                    >
                      <i className={`las la-pen`} />
                    </button>
                  </>
                )}
              </div>

              <div className={`track-buttons`}>
                <button
                  className={`btn btn-sm btn-outline-danger remove-track`}
                  type={"button"}
                  onClick={(e) => onClickRemoveTrack(e)}
                >
                  <i className={`las la-trash`} />
                </button>

                <button
                  className={`btn btn-sm btn-primary`}
                  type={"button"}
                  onClick={(e) => onClickAddSegment(e)}
                >
                  <i className={`las la-plus`} /> Segment
                </button>
              </div>
            </>
          )}
        </div>
      )}

      {showSegments && (
        <div
          className={`segments`}
          style={{
            "--segments-padding-left": `${paddingLeft}px`,
            "--segments-padding-right": `${paddingRight}px`,
          }}
        >
          {Object.entries(annotationTrack.segments).map(
            ([segmentIndex, segment]) => {
              return (
                <TrackSegment
                  duration={duration}
                  isSelectedAnnotationTrack={isSelectedAnnotationTrack}
                  key={`track-segment-${segmentIndex}`}
                  onClickSegment={onClickSegment}
                  paddingLeft={paddingLeft}
                  playerSizes={playerSizes}
                  segment={segment}
                  segmentIndex={segmentIndex}
                  segmentsColor={segmentsColor}
                  selectedSegment={selectedSegment}
                />
              );
            }
          )}
        </div>
      )}

      {showSegmentToChangeInfo && (
        <div className={`segment-info`}>
          <div className={`time`}>
            <span>Time:</span>

            <input
              className={`form-control form-control-sm`}
              placeholder={"Start"}
              readOnly={true}
              value={secontsToTime(segmentToChange.start_sec)}
            />

            {!inReviewState && (
              <button
                className={`btn btn-sm btn-outline-dark`}
                type={"button"}
                onClick={(e) =>
                  onClickSaveFormField(e, "start_sec", player.currentTime())
                }
                title={"Save current player time as a start of this section"}
              >
                <i className={`las la-thumbtack`} />
              </button>
            )}

            <span>-</span>

            <input
              className={`form-control form-control-sm`}
              placeholder={"End"}
              readOnly={true}
              value={secontsToTime(segmentToChange.end_sec)}
            />

            {!inReviewState && (
              <button
                className={`btn btn-sm btn-outline-dark`}
                type={"button"}
                onClick={(e) =>
                  onClickSaveFormField(e, "end_sec", player.currentTime())
                }
                title={"Save current player time as an end of this section"}
              >
                <i className={`las la-thumbtack`} />
              </button>
            )}
          </div>

          <div className="form-label-group">
            <input
              className={`form-control form-control-sm`}
              id={"id_segment_name"}
              name={"segment_name"}
              placeholder={" "} // Must be a string with space for floating label
              value={segmentToChange.title}
              onChange={(e) => onClickSaveFormField(e, "title", e.target.value)}
              readOnly={inReviewState}
            />

            <label htmlFor={"id_segment_name"}>Segment name</label>
          </div>

          <div className="form-label-group">
            <textarea
              className={`form-control form-control-sm`}
              id={"id_segment_description"}
              name={"segment_description"}
              rows={"3"}
              placeholder={" "} // Must be a string with space for floating label
              value={segmentToChange.description}
              onChange={(e) =>
                onClickSaveFormField(e, "description", e.target.value)
              }
              readOnly={inReviewState}
            />

            <label htmlFor={"id_segment_description"}>
              Describe what you see in this segment
            </label>
          </div>

          {!inReviewState && (
            <div className={`segment-buttons`}>
              <button
                className={`btn btn-sm btn-outline-danger remove-segment`}
                type={"button"}
                onClick={(e) => onClickRemoveSegment(e)}
                title={"Remove this segment"}
              >
                <i className={`las la-trash`} />
              </button>

              <button
                className={`btn btn-sm btn-outline-dark`}
                type={"button"}
                onClick={(e) => onClickRestoreOldSegmentData(e)}
                title={"Restore all fields from previous saving"}
              >
                <i className={`las la-redo-alt`} />
              </button>

              <button
                className={`btn btn-sm btn-success`}
                type={"button"}
                onClick={(e) => onClickSaveSegmentData(e)}
                title={"Save current data"}
              >
                <i className={`las la-save`} />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default AnnotationTrack;
