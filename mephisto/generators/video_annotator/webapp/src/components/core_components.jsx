/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import {
  VideoAnnotator,
  prepareRemoteProcedures,
  prepareVideoAnnotatorData,
} from "mephisto-task-addons";
import * as customValidators from "custom-validators";
import * as customTriggers from "custom-triggers";

function LoadingScreen() {
  return <Directions>Loading...</Directions>;
}

function LoadingPresignedUrlsScreen() {
  return <Directions>Please wait, rendering Video Annotator...</Directions>;
}

function NoDataErrorsMessage() {
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
  const [loadingData, setLoadingData] = React.useState(false);
  const [renderingErrors, setRenderingErrors] = React.useState(null);
  const [annotatorData, setAnnotatorData] = React.useState(null);

  const inReviewState = finalResults !== null;
  const initialConfigAnnotatorData = taskData.annotator;

  if (!inReviewState) {
    prepareRemoteProcedures(remoteProcedure);
  }

  // ----- Effects -----

  React.useEffect(() => {
    if (inReviewState) {
      setAnnotatorData(initialConfigAnnotatorData);
    } else {
      prepareVideoAnnotatorData(
        taskData,
        setAnnotatorData,
        setLoadingData,
        setRenderingErrors
      );
    }
  }, [taskData.annotator]);

  if (!initialConfigAnnotatorData) {
    return <NoDataErrorsMessage />;
  }

  if (loadingData) {
    return <LoadingPresignedUrlsScreen />;
  }

  if (renderingErrors) {
    return <RenderingErrorsMessage />;
  }

  return (
    <div>
      {annotatorData && (
        <VideoAnnotator
          data={annotatorData}
          onSubmit={(data) => onSubmit({ tracks: data })}
          finalResults={finalResults}
          setRenderingErrors={setRenderingErrors}
          customValidators={customValidators}
          customTriggers={customTriggers}
        />
      )}
    </div>
  );
}

export { LoadingScreen, VideoAnnotatorBaseFrontend };
