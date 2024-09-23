/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import { getFormatStringWithTokensFunction } from "../FormComposer/utils";
import TaskInstructionButton from "../TaskInstructionModal/TaskInstructionButton";
import TaskInstructionModal from "../TaskInstructionModal/TaskInstructionModal";
import AnnotationTracks from "./AnnotationTracks.jsx";
import "./VideoAnnotator.css";
import VideoPlayer from "./VideoPlayer.jsx";

const DELAY_PROGRESSBAR_RESIZING_MSEC = 1000;

const STORAGE_PRESAVED_ANNOTATION_TRACKS_KEY = "annotation_tracks";

// In case if user does not specify any field
const DEFAULT_SEGMENT_FIELDS = [
  {
    id: "id_title",
    label: "Segment name",
    name: "title",
    type: "input",
  },
];

function VideoAnnotator({
  data,
  onSubmit,
  finalResults = null,
  setRenderingErrors,
  customValidators,
  customTriggers,
}) {
  const videoAnnotatorConfig = data;

  // State to hide submit button
  const [onSubmitLoading, setOnSubmitLoading] = React.useState(false);

  // Annotator instruction modal state
  const [
    annotatorInstrupctionModalOpen,
    setAnnotatorInstrupctionModalOpen,
  ] = React.useState(false);

  const inReviewState = finalResults !== null;

  const formatStringWithTokens = getFormatStringWithTokensFunction(
    inReviewState
  );

  const playerRef = React.useRef(null);

  const [videoPlayerChapters, setVideoPlayerChapters] = React.useState([]);

  const [annotationTracksData, setAnnotationTracksData] = React.useState([]);

  const [segmentValidation, setSegmentValidation] = React.useState({});

  let initialAnnotationTracksData = [];
  if (inReviewState) {
    initialAnnotationTracksData = finalResults?.tracks;
  } else {
    try {
      const presavedAnnotationTracks = JSON.parse(
        localStorage.getItem(STORAGE_PRESAVED_ANNOTATION_TRACKS_KEY)
      );
      initialAnnotationTracksData = presavedAnnotationTracks || [];
    } catch (e) {
      console.warn("Cannot read presaved annotation tracks");
      // Remove incorrect data from local storage
      localStorage.removeItem(STORAGE_PRESAVED_ANNOTATION_TRACKS_KEY);
    }
  }

  const [playerSizes, setPlayerSizes] = React.useState({
    player: {},
    progressBar: {},
  });
  const [duration, setDuration] = React.useState(0);

  let annotatorSubmitButton = videoAnnotatorConfig.submit_button;

  let showTaskInstructionAsModal =
    videoAnnotatorConfig.show_instructions_as_modal || false;

  let annotatorTitle = formatStringWithTokens(
    videoAnnotatorConfig?.title || "",
    setRenderingErrors
  );
  let annotatorInstruction = formatStringWithTokens(
    videoAnnotatorConfig?.instruction || "",
    setRenderingErrors
  );
  const segmentIsValid = Object.keys(segmentValidation).length === 0;

  let segmentFields = videoAnnotatorConfig.segment_fields;
  if (!segmentFields || segmentFields.length === 0) {
    segmentFields = DEFAULT_SEGMENT_FIELDS;
  }

  const videoJsOptions = {
    autoplay: false,
    controls: true,
    sources: [
      {
        src: videoAnnotatorConfig.video,
        type: "video/mp4",
      },
    ],
    width: "700",
    height: "400",
    playbackRates: [0.5, 1, 1.5, 2],
    preload: "auto",
    controlBar: {
      fullscreenToggle: false,
      pictureInPictureToggle: false,
    },
    inactivityTimeout: 0,
  };

  // ----- Methods -----

  function updatePlayerSizes() {
    const videoPlayer = document.getElementsByClassName("video-js")[0];
    const progressBar = document.getElementsByClassName(
      "vjs-progress-holder"
    )[0];

    if (videoPlayer && progressBar) {
      setPlayerSizes({
        player: videoPlayer.getBoundingClientRect(),
        progressBar: progressBar.getBoundingClientRect(),
      });
    }
  }

  function onVideoPlayerReady(player) {
    playerRef.current = player;

    updatePlayerSizes();

    // Right after player is ready sometimes size of progress bar is not correct,
    // because some elements on the right side are still loading
    setTimeout(() => updatePlayerSizes(), DELAY_PROGRESSBAR_RESIZING_MSEC);

    // Set video duration
    player.on("loadedmetadata", () => {
      setDuration(player.duration());
    });

    // Stop playing the video at the end of the selected segment
    player.on("timeupdate", () => {
      // HACK to pass values into event listeners as them cannot read updated React states
      const sectionElement = document.querySelectorAll(`.segment.active`)[0];
      if (!sectionElement) {
        return;
      }
      const endSec = Number.parseFloat(sectionElement.dataset.endsec) || null;
      if (endSec === null) {
        return;
      }

      // Check for end only if video is playing
      const isVideoPlaying = !!(
        player.currentTime() > 0 &&
        !player.paused() &&
        !player.ended() &&
        player.readyState() > 2
      );
      if (isVideoPlaying) {
        if (player.currentTime() >= endSec) {
          player.pause();
          // HACK: setting exact end value on progress bar,
          // because this event is being fired every 15-250 milliseconds,
          // and it can be further than real value
          player.currentTime(endSec);
        }
      }
    });

    // Resize track segment if progress bar changes its width
    const playerProgressBarResizeObserver = new ResizeObserver(() => {
      updatePlayerSizes();
    });

    const progressBarElement = player.controlBar.progressControl.el_;
    if (progressBarElement) {
      playerProgressBarResizeObserver.observe(progressBarElement);
    }
  }

  function onSelectSegment(segment) {
    const player = playerRef.current;

    // Set start
    if (player) {
      const startTime = segment?.start_sec || 0;
      player.currentTime(startTime);
    }
  }

  function onChangeAnnotationTracks(data) {
    setAnnotationTracksData(data);
    localStorage.setItem(
      STORAGE_PRESAVED_ANNOTATION_TRACKS_KEY,
      JSON.stringify(data)
    );
  }

  function onSubmitAnnotation(e) {
    e.preventDefault();
    e.stopPropagation();

    // Pass data to `mephisto-task` library
    setOnSubmitLoading(true);
    onSubmit(annotationTracksData);

    // Clean presaved data, because it was already sent to the server
    localStorage.removeItem(STORAGE_PRESAVED_ANNOTATION_TRACKS_KEY);
  }

  return (
    <div className={`video-annotation`}>
      {/* Task info */}
      <h2 className={`title`}>{annotatorTitle}</h2>

      {/* Show instruction or button that opens a modal with instructions */}
      {showTaskInstructionAsModal ? (
        <>
          {/* Instructions */}
          {annotatorTitle && annotatorInstruction && <hr />}

          {annotatorInstruction && (
            <div className={`instruction-hint`}>
              For instructions, click "Task Instruction" button in the top-right
              corner.
            </div>
          )}

          {/* Button (modal in the end of the component) */}
          <TaskInstructionButton
            onClick={() =>
              setAnnotatorInstrupctionModalOpen(!annotatorInstrupctionModalOpen)
            }
          />
        </>
      ) : (
        <>
          {/* Instructions */}
          {annotatorTitle && annotatorInstruction && <hr />}

          {annotatorInstruction && (
            <div
              className={`instruction`}
              dangerouslySetInnerHTML={{ __html: annotatorInstruction || "" }}
            ></div>
          )}
        </>
      )}

      {/* Video Player */}
      <div className={"video-player"}>
        <VideoPlayer
          chapters={videoPlayerChapters}
          onReady={onVideoPlayerReady}
          options={videoJsOptions}
        />
      </div>

      {/* Annotations */}
      <AnnotationTracks
        customTriggers={customTriggers}
        customValidators={customValidators}
        duration={duration}
        formatStringWithTokens={formatStringWithTokens}
        inReviewState={inReviewState}
        onChange={onChangeAnnotationTracks}
        onSelectSegment={onSelectSegment}
        player={playerRef.current}
        playerSizes={playerSizes}
        segmentFields={segmentFields}
        segmentIsValid={segmentIsValid}
        segmentValidation={segmentValidation}
        setRenderingErrors={setRenderingErrors}
        setSegmentValidation={setSegmentValidation}
        setVideoPlayerChapters={setVideoPlayerChapters}
        tracks={initialAnnotationTracksData}
      />

      {/* Submit button */}
      {annotatorSubmitButton && !inReviewState && (
        <div
          className={`${annotatorSubmitButton.classes || ""}`}
          id={annotatorSubmitButton.id}
        >
          <hr className={`annotator-buttons-separator`} />

          {onSubmitLoading ? (
            // Banner of success
            <div
              className={`alert alert-success centered mx-auto col-6 ml-2 mr-2`}
            >
              Thank you!
              <br />
              Your form has been submitted.
            </div>
          ) : (
            <>
              {/* Button instruction */}
              {annotatorSubmitButton.instruction && (
                <div
                  className={`alert alert-light centered mx-auto col-6 ml-2 mr-2`}
                  dangerouslySetInnerHTML={{
                    __html: annotatorSubmitButton.instruction,
                  }}
                ></div>
              )}

              {/* Submit button */}
              <div className={`annotator-buttons container`}>
                <button
                  className={`button-submit btn btn-success`}
                  type={"submit"}
                  title={annotatorSubmitButton.tooltip}
                  onClick={(e) => segmentIsValid && onSubmitAnnotation(e)}
                  disabled={!segmentIsValid}
                >
                  {annotatorSubmitButton.text}
                </button>
              </div>
            </>
          )}
        </div>
      )}

      {/* Modal with task instructions */}
      {showTaskInstructionAsModal && annotatorInstruction && (
        <TaskInstructionModal
          classNameDialog={`annotator-instruction-dialog`}
          instructions={
            <p dangerouslySetInnerHTML={{ __html: annotatorInstruction }}></p>
          }
          open={annotatorInstrupctionModalOpen}
          setOpen={setAnnotatorInstrupctionModalOpen}
          title={"Task Instructions"}
        />
      )}
    </div>
  );
}

export default VideoAnnotator;
