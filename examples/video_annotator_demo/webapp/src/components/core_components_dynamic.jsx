/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import { VideoAnnotator } from "mephisto-task-addons";

// Required import for custom validators
import * as customValidators from "custom-validators";
// Required import for custom triggers
import * as customTriggers from "custom-triggers";

function LoadingScreen() {
  return <Directions>Loading...</Directions>;
}

function Directions({ children }) {
  return (
    <div className="card mb-4">
      <div className="card-body container">{children}</div>
    </div>
  );
}

function VideoAnnotatorBaseFrontend({
  taskData,
  onSubmit,
  onError,
  finalResults = null,
}) {
  const initialConfigAnnotatorData = taskData.annotator;

  if (!initialConfigAnnotatorData) {
    return (
      <div>
        Passed video annotator data is invalid... Recheck your task config.
      </div>
    );
  }

  return (
    <div>
      <VideoAnnotator
        data={initialConfigAnnotatorData}
        onSubmit={(data) => onSubmit({ tracks: data })}
        finalResults={finalResults}
        // Required for custom validators
        customValidators={customValidators}
        // Required for custom triggers
        customTriggers={customTriggers}
      />
    </div>
  );
}

export { LoadingScreen, VideoAnnotatorBaseFrontend };
