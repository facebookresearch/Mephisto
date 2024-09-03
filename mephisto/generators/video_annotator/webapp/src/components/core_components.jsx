/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import {
  prepareFormData,
  prepareRemoteProcedures,
  TaskInstructionButton,
  TaskInstructionModal,
} from "mephisto-task-addons";
import * as customValidators from "custom-validators";
import * as customTriggers from "custom-triggers";
import AnnotationTracks from "./AnnotationTracks.jsx";
import VideoPlayer from "./VideoPlayer.jsx";

const DELAY_PROGRESSBAR_RESIZING_MSEC = 1000;

function LoadingScreen() {
  return <Directions>Loading...</Directions>;
}

function LoadingPresignedUrlsScreen() {
  return <Directions>Please wait, rendering Video Annotator...</Directions>;
}

function NoAnnotatorDataErrorsMessage() {
  return (
    <div>
      Could not render the form due to invalid configuration. We're sorry,
      please return the task.
    </div>
  );
}

function RenderingErrorsMessage() {
  return (
    <div>
      Sorry, we could not render the page. Please try to restart this task (or
      cancel it).
    </div>
  );
}

function Directions({ children }) {
  return (
    <section className="hero is-light" data-cy="directions-container">
      <div className="hero-body">
        <div className="container">
          <p className="subtitle is-5">{children}</p>
        </div>
      </div>
    </section>
  );
}

function VideoAnnotatorBaseFrontend({
  taskData,
  onSubmit,
  onError,
  finalResults = null,
  remoteProcedure,
}) {
  const [loadingAnnotatorData, setLoadingAnnotatorData] = React.useState(false);
  const [annotatorData, setAnnotatorData] = React.useState(null);
  const [
    videoAnnotatorRenderingErrors,
    setVideoAnnotatorRenderingErrors,
  ] = React.useState(null);

  // State to hide submit button
  const [onSubmitLoading, setOnSubmitLoading] = React.useState(false);

  // Annotator instruction modal state
  const [
    annotatorInstrupctionModalOpen,
    setAnnotatorInstrupctionModalOpen,
  ] = React.useState(false);

  const inReviewState = finalResults !== null;
  const initialConfigAnnotatorData = taskData.annotator;

  if (!inReviewState) {
    prepareRemoteProcedures(remoteProcedure);
  }

  const playerRef = React.useRef(null);

  const [videoPlayerChapters, setVideoPlayerChapters] = React.useState([]);

  const [annotationTracksData, setAnnotationTracksData] = React.useState([]);

  const [segmentValidation, setSegmentValidation] = React.useState({});

  const initialAnnotationTracksData = finalResults || [];

  const [playerSizes, setPlayerSizes] = React.useState({
    player: {},
    progressBar: {},
  });
  const [duration, setDuration] = React.useState(0);

  let annotatorSubmitButton = initialConfigAnnotatorData.submit_button;

  let showTaskInstructionAsModal =
    initialConfigAnnotatorData.show_instructions_as_modal || false;

  let annotatorTitle = annotatorData?.title || "";
  let annotatorInstruction = annotatorData?.instruction || "";
  const segmentIsValid = Object.keys(segmentValidation).length === 0;

  const videoJsOptions = {
    autoplay: false,
    controls: true,
    sources: [
      {
        src: initialConfigAnnotatorData.video,
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
    const startTime = segment?.start_sec || 0;
    player.currentTime(startTime);
  }

  function onChangeAnnotationTracks(data) {
    setAnnotationTracksData(data);
  }

  function onSubmitAnnotation(e) {
    e.preventDefault();
    e.stopPropagation();

    // Pass data to `mephisto-task` library
    setOnSubmitLoading(true);
    onSubmit(annotationTracksData);
  }

  // ----- Effects -----

  React.useEffect(() => {
    if (inReviewState) {
      setAnnotatorData(initialConfigAnnotatorData);
    } else {
      // TODO
      setAnnotatorData(initialConfigAnnotatorData);
      // prepareFormData(
      //   taskData,
      //   setAnnotatorData,
      //   setLoadingFormData,
      //   setFormComposerRenderingErrors
      // );
    }
  }, [taskData.annotator]);

  if (!initialConfigAnnotatorData) {
    return <NoAnnotatorDataErrorsMessage />;
  }

  if (loadingAnnotatorData) {
    return <LoadingPresignedUrlsScreen />;
  }

  if (videoAnnotatorRenderingErrors) {
    return <RenderingErrorsMessage />;
  }

  return (
    <div className={`video-annotation`}>
      {/* Task info */}
      <h2 className={`title`}>{annotatorData?.title}</h2>

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
        duration={duration}
        inReviewState={inReviewState}
        onChange={onChangeAnnotationTracks}
        onSelectSegment={onSelectSegment}
        player={playerRef.current}
        playerSizes={playerSizes}
        segmentIsValid={segmentIsValid}
        segmentValidation={segmentValidation}
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

export { LoadingScreen, VideoAnnotatorBaseFrontend };
