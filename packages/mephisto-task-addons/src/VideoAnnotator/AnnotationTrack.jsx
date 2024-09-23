/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { cloneDeep } from "lodash";
import React from "react";
import { FieldType } from "../FormComposer/constants";
import { validateFormFields } from "../FormComposer/validation/helpers";
import { FormComposerFields, ListErrors } from "../index.jsx";
import "./AnnotationTrack.css";
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

  const showSegments = !!Object.keys(annotationTrack.segments).length;

  const segmentFieldsByName = Object.fromEntries(
    segmentFields.map((x) => [x.name, x])
  );

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
    newSegment.title = `Segment #${segmentsCount + 1} `;

    if (segmentsCount !== 0) {
      const latestSegment = annotationTrack.segments[segmentsCount - 1];
      newSegment.start_sec =
        latestSegment.end_sec + START_NEXT_SECTION_PLUS_SEC;
      newSegment.end_sec = newSegment.start_sec;

      // Prevent creating empty duplicates
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
  }

  function validateTimeFieldsOnSave() {
    const errors = [];
    const validation = {};

    // If start is greater than end
    if (segmentToChange.start_sec > segmentToChange.end_sec) {
      errors.push(`Start of the section cannot be greater than end of it.`);
      validation.end_sec = false;
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
        validation.start_sec = false;
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
        validation.end_sec = false;
      }
    });

    // Update segment validation results
    setSegmentValidation(validation);

    return errors;
  }

  function onClickSegment(e, segmentIndex) {
    player.pause();
    setTimeout(
      () => setSelectedSegment(segmentIndex),
      DELAY_CLICK_ON_SECTION_MSEC
    );
  }

  function onClickSaveFormField(fieldName, value, e) {
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
    let _segmentToChange = null;

    if (selectedSegment !== null) {
      _segmentToChange = annotationTrack.segments[selectedSegment];
      setSegmentToChange(_segmentToChange);
    }

    onSelectSegment && onSelectSegment(_segmentToChange);
  }, [selectedSegment]);

  React.useEffect(() => {
    if (!segmentToChange) {
      return;
    }

    // Validate current segment
    const timeFieldsErrors = validateTimeFieldsOnSave();
    setSegmentToChangeErrors(timeFieldsErrors);

    // Validate dynamic segment fields
    const dynamicFieldsErrorsByField = validateFormFields(
      segmentToChange,
      segmentFieldsByName,
      customValidators
    );
    setInvalidSegmentFields(dynamicFieldsErrorsByField);

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
                  onClick={(e) => segmentIsValid && onClickAddSegment(e)}
                  disabled={!segmentIsValid}
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
                  onClickSaveFormField(
                    "start_sec",
                    player ? player.currentTime() : 0,
                    e
                  )
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
                  onClickSaveFormField(
                    "end_sec",
                    player ? player.currentTime() : 0,
                    e
                  )
                }
                title={"Save current player time as an end of this section"}
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
                      updateFormData={onClickSaveFormField}
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
                      updateFormData={onClickSaveFormField}
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
                      updateFormData={onClickSaveFormField}
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
                      updateFormData={onClickSaveFormField}
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
                      updateFormData={onClickSaveFormField}
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
