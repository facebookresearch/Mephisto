/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { cloneDeep } from "lodash";
import React from "react";
import { FieldType } from "../FormComposer/constants";
import { validateFormFields } from "../FormComposer/validation/helpers";
import { pluralizeString } from "../helpers";
import { FormComposerFields, ListErrors } from "../index.jsx";
import "./AnnotationTrack.css";
import {
  COLORS,
  DELAY_CLICK_ON_SECTION_MSEC,
  DELAY_SHOW_OVERLAPPING_MESSAGE_MSEC,
  POPOVER_INVALID_SEGMENT_CLASS,
  POPOVER_INVALID_SEGMENT_PROPS,
  START_NEXT_SECTION_PLUS_SEC,
} from "./constants";
import { secontsToTime } from "./helpers";
import TrackSegment from "./TrackSegment.jsx";
import { validateTimeFieldsOnSave } from "./utils";

function AnnotationTrack({
  annotationTrack,
  customTriggers,
  customValidators,
  duration,
  formatStringWithTokens,
  inReviewState,
  onClickAnnotationTrack,
  onSelectSegment,
  player,
  playerSizes,
  segmentFields,
  segmentIsValid,
  segmentValidation,
  selectedAnnotationTrack,
  setAnnotationTracks,
  setRenderingErrors,
  setSegmentValidation,
  trackIndex,
}) {
  const [trackTitle, setTrackTitle] = React.useState(annotationTrack.title);

  const [inEditState, setInEditState] = React.useState(false);
  const [selectedSegment, setSelectedSegment] = React.useState(null);
  const [
    overlappingSegmentErrors,
    setOverlappingSegmentErrors,
  ] = React.useState([]);
  const [segmentToChangeErrors, setSegmentToChangeErrors] = React.useState([]);
  const [segmentToChange, setSegmentToChange] = React.useState(null);
  // Invalid fields (having error messages after form validation)
  const [invalidSegmentFields, setInvalidSegmentFields] = React.useState({});

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

  const showSegments = true;

  const segmentFieldsByName = Object.fromEntries(
    segmentFields.map((x) => [x.name, x])
  );

  const segmentsAmount = Object.keys(annotationTrack.segments).length;

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
      setSegmentValidation({});
      setOverlappingSegmentErrors([]);
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
      setSegmentValidation({});
      setOverlappingSegmentErrors([]);
    }
  }

  function getCleanSegmentToChangeData() {
    const typeDefaultValueMapping = {
      [FieldType.CHECKBOX]: null,
      [FieldType.EMAIL]: "",
      [FieldType.FILE]: "",
      [FieldType.HIDDEN]: "",
      [FieldType.INPUT]: "",
      [FieldType.NUMBER]: "",
      [FieldType.PASSWORD]: "",
      [FieldType.RADIO]: null,
      [FieldType.SELECT]: null,
      [FieldType.TEXTAREA]: "",
    };
    const _segmentToChange = {};
    segmentFields.map((field, i) => {
      const fieldDefaultValue = typeDefaultValueMapping[field.type] || "";
      _segmentToChange[field.name] = fieldDefaultValue;
    });

    return _segmentToChange;
  }

  function onClickAddSegment(e) {
    const segmentsCount = Object.keys(annotationTrack.segments).length;

    const newSegment = cloneDeep(getCleanSegmentToChangeData());
    newSegment.title = `Segment #${segmentsCount + 1}`;

    // Get current video time and set it to new segment
    let currentVideoTime = null;
    if (player) {
      currentVideoTime = player.currentTime() + START_NEXT_SECTION_PLUS_SEC;
    }
    newSegment.start_sec = currentVideoTime;
    newSegment.end_sec = currentVideoTime;

    if (segmentsCount !== 0) {
      const latestSegment = annotationTrack.segments[segmentsCount - 1];

      // In case if player was not found somehow, create segment right after previous one
      if (currentVideoTime === null) {
        currentVideoTime = latestSegment.end_sec + START_NEXT_SECTION_PLUS_SEC;
        newSegment.start_sec = currentVideoTime;
        newSegment.end_sec = currentVideoTime;
      }

      // Prevent creating empty duplicates with unset time fields
      if (latestSegment.start_sec === newSegment.start_sec) {
        alert(
          "You already have unfinished segment.\n\n" +
            "Change it or remove to created another new one."
        );
        return;
      }
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

    setSelectedSegment(newSegmentIndex);
    setSegmentToChange(newSegment);
    onSelectSegment && onSelectSegment(newSegment);

    // Show overlapping message under segments progress bar
    const timeFieldsValidationResults = validateTimeFieldsOnSave(
      annotationTrack,
      newSegment,
      newSegmentIndex
    );
    if (timeFieldsValidationResults.errors.length > 0) {
      setTimeout(() => {
        setOverlappingSegmentErrors([
          "Overlapping segment should be added to a different track",
        ]);
      }, DELAY_SHOW_OVERLAPPING_MESSAGE_MSEC);
    }
  }

  function onClickSegment(e, segmentIndex) {
    player.pause();
    setTimeout(() => {
      setSelectedSegment(segmentIndex);
      const segment = annotationTrack.segments[segmentIndex];
      setSegmentToChange(segment);
      onSelectSegment && onSelectSegment(segment);
    }, DELAY_CLICK_ON_SECTION_MSEC);
  }

  function updateSegmentToChangeFormData(fieldName, value, e) {
    if (e) {
      e.preventDefault();
    }

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
    if (!segmentToChange) {
      return;
    }

    // Validate current segment
    const timeFieldsValidationResults = validateTimeFieldsOnSave(
      annotationTrack,
      segmentToChange,
      selectedSegment
    );
    setSegmentValidation(timeFieldsValidationResults.fields);
    setSegmentToChangeErrors(timeFieldsValidationResults.errors);

    // Validate dynamic segment fields
    const dynamicFieldsErrorsByField = validateFormFields(
      segmentToChange,
      segmentFieldsByName,
      customValidators
    );
    setInvalidSegmentFields(dynamicFieldsErrorsByField);

    // Clean overlapping message
    setOverlappingSegmentErrors([]);

    // Update segment validation results
    setSegmentValidation((prevState) => {
      return {
        ...prevState,
        ...dynamicFieldsErrorsByField,
      };
    });

    // Save current segment
    setAnnotationTracks((prevState) => {
      const prevAnnotationTrack = cloneDeep(prevState[trackIndex]);
      prevAnnotationTrack.segments[selectedSegment] = segmentToChange;
      return {
        ...prevState,
        ...{ [trackIndex]: prevAnnotationTrack },
      };
    });
  }, [segmentToChange]);

  return (
    <div
      className={`
        annotation-track
        ${isSelectedAnnotationTrack ? "active" : ""}
        ${!segmentIsValid ? "non-clickable" : ""}
        ${POPOVER_INVALID_SEGMENT_CLASS}
      `}
      onClick={(e) => segmentIsValid && onClickTrack(e)}
      {...POPOVER_INVALID_SEGMENT_PROPS}
    >
      {/* Short name on unactive track */}
      {!isSelectedAnnotationTrack && (
        <>
          <div className={`track-name-small`}>{annotationTrack.title}</div>

          <div className={`segments-count`}>
            {segmentsAmount} {pluralizeString("segment", segmentsAmount)}
          </div>
        </>
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
                      <i className={`las la-pen`} /> Track
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
                  <i className={`las la-trash`} /> Track
                </button>

                <button
                  className={`btn btn-sm btn-primary ${POPOVER_INVALID_SEGMENT_CLASS}`}
                  type={"button"}
                  onClick={(e) => segmentIsValid && onClickAddSegment(e)}
                  disabled={!segmentIsValid}
                  {...POPOVER_INVALID_SEGMENT_PROPS}
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
          <div
            className={`progress-bar`}
            style={{
              "--segments-padding-left": `${paddingLeft}px`,
              "--segments-padding-right": `${paddingRight}px`,
            }}
          />

          {Object.entries(annotationTrack.segments).map(
            ([segmentIndex, segment]) => {
              return (
                <TrackSegment
                  duration={duration}
                  isSelectedAnnotationTrack={isSelectedAnnotationTrack}
                  key={`track-segment-${segmentIndex}`}
                  onClickSegment={(e, index) =>
                    segmentIsValid && onClickSegment(e, index)
                  }
                  paddingLeft={paddingLeft}
                  playerSizes={playerSizes}
                  segment={segment}
                  segmentIndex={segmentIndex}
                  segmentIsValid={segmentIsValid}
                  segmentsColor={segmentsColor}
                  selectedSegment={selectedSegment}
                />
              );
            }
          )}
        </div>
      )}

      <ListErrors
        className={`
          overlapping-segments
          ${overlappingSegmentErrors.length ? "is-invalid" : ""}
        `}
        messages={overlappingSegmentErrors}
      />

      {showSegmentToChangeInfo && (
        <div
          className={`
            segment-info
            ${segmentToChangeErrors.length ? "is-invalid" : ""}
          `}
        >
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
                  updateSegmentToChangeFormData(
                    "start_sec",
                    player ? player.currentTime() : 0,
                    e
                  )
                }
                title={"Save current player time as a start of this segment"}
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
                  updateSegmentToChangeFormData(
                    "end_sec",
                    player ? player.currentTime() : 0,
                    e
                  )
                }
                title={"Save current player time as an end of this segment"}
              >
                <i className={`las la-thumbtack`} />
              </button>
            )}
          </div>

          {/* Time fields errors */}
          <ListErrors messages={segmentToChangeErrors} />

          {segmentFields.map((field, fieldIndex) => {
            const _field = {
              ...field,
              placeholder: " ", // Must be a string with space for floating label
            };

            const fieldLabel = formatStringWithTokens(
              _field.label,
              setRenderingErrors
            );
            const fieldTooltip = formatStringWithTokens(
              _field.tooltip,
              setRenderingErrors
            );

            const fieldHelp = _field.help;

            const useFloatingLabel = [
              FieldType.INPUT,
              FieldType.EMAIL,
              FieldType.PASSWORD,
              FieldType.NUMBER,
              FieldType.TEXTAREA,
            ].includes(_field.type);

            const isInvalid = !!(invalidSegmentFields[_field.name] || [])
              .length;
            const validationErrors = invalidSegmentFields[_field.name] || [];

            return (
              <React.Fragment
                key={`segment-field-${_field.type}-${fieldIndex}`}
              >
                <div
                  className={`form-label-group ${
                    useFloatingLabel ? "floating-label" : ""
                  }`}
                  title={fieldTooltip}
                >
                  {!useFloatingLabel && (
                    <label className={`field-label`} htmlFor={_field.id}>
                      {fieldLabel}
                    </label>
                  )}

                  {[
                    FieldType.INPUT,
                    FieldType.EMAIL,
                    FieldType.PASSWORD,
                    FieldType.NUMBER,
                  ].includes(_field.type) && (
                    <FormComposerFields.InputField
                      className={`form-control-sm`}
                      field={_field}
                      formData={segmentToChange}
                      updateFormData={updateSegmentToChangeFormData}
                      disabled={inReviewState}
                      initialFormData={segmentToChange}
                      inReviewState={inReviewState}
                      invalid={isInvalid}
                      validationErrors={validationErrors}
                      formFields={segmentFieldsByName}
                      customTriggers={customTriggers}
                    />
                  )}

                  {_field.type === FieldType.TEXTAREA && (
                    <FormComposerFields.TextareaField
                      className={`form-control-sm`}
                      field={_field}
                      formData={segmentToChange}
                      updateFormData={updateSegmentToChangeFormData}
                      disabled={inReviewState}
                      initialFormData={segmentToChange}
                      inReviewState={inReviewState}
                      invalid={isInvalid}
                      validationErrors={validationErrors}
                      formFields={segmentFieldsByName}
                      customTriggers={customTriggers}
                      rows={"3"}
                    />
                  )}

                  {_field.type === FieldType.CHECKBOX && (
                    <FormComposerFields.CheckboxField
                      field={_field}
                      formData={segmentToChange}
                      updateFormData={updateSegmentToChangeFormData}
                      disabled={inReviewState}
                      initialFormData={segmentToChange}
                      inReviewState={inReviewState}
                      invalid={isInvalid}
                      validationErrors={validationErrors}
                      formFields={segmentFieldsByName}
                      customTriggers={customTriggers}
                    />
                  )}

                  {_field.type === FieldType.RADIO && (
                    <FormComposerFields.RadioField
                      field={_field}
                      formData={segmentToChange}
                      updateFormData={updateSegmentToChangeFormData}
                      disabled={inReviewState}
                      initialFormData={segmentToChange}
                      inReviewState={inReviewState}
                      invalid={isInvalid}
                      validationErrors={validationErrors}
                      formFields={segmentFieldsByName}
                      customTriggers={customTriggers}
                    />
                  )}

                  {_field.type === FieldType.SELECT && (
                    <FormComposerFields.SelectField
                      field={_field}
                      formData={segmentToChange}
                      updateFormData={updateSegmentToChangeFormData}
                      disabled={inReviewState}
                      initialFormData={segmentToChange}
                      inReviewState={inReviewState}
                      invalid={isInvalid}
                      validationErrors={validationErrors}
                      formFields={segmentFieldsByName}
                      customTriggers={customTriggers}
                    />
                  )}

                  {useFloatingLabel && (
                    <label htmlFor={_field.id}>{fieldLabel}</label>
                  )}

                  {fieldHelp && (
                    <small
                      className={`field-help form-text text-muted`}
                      dangerouslySetInnerHTML={{
                        __html: fieldHelp,
                      }}
                    />
                  )}
                </div>
              </React.Fragment>
            );
          })}

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
            </div>
          )}

          {/*<ListErrors messages={segmentToChangeErrors} />*/}
        </div>
      )}
    </div>
  );
}

export default AnnotationTrack;
