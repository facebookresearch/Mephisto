/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { VideoAnnotator } from "mephisto-task-addons";
import React from "react";

function LoadingScreen() {
  return <Directions>Loading...</Directions>;
}

function Directions({ children }) {
  return (
    <section className="text-center" data-cy="directions-container">
      <div className="alert alert-primary">
        <div className="container">
          <h2>{children}</h2>
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
      />
    </div>
  );
}

export { VideoAnnotatorBaseFrontend, LoadingScreen };
