/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import {
  FormComposer,
  prepareFormData,
  prepareRemoteProcedures,
} from "mephisto-addons";

function LoadingScreen() {
  return <Directions>Loading...</Directions>;
}

function LoadingPresignedUrlsScreen() {
  return <Directions>Please wait, rendering form...</Directions>;
}

function NoFormDataErrorsMessage() {
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
    <div className="card mb-4">
      <div className="card-body container">{children}</div>
    </div>
  );
}

function FormComposerBaseFrontend({
  taskData,
  onSubmit,
  onError,
  finalResults = null,
  remoteProcedure,
}) {
  const [loadingFormData, setLoadingFormData] = React.useState(false);
  const [formData, setFormData] = React.useState(null);
  const [
    formComposerRenderingErrors,
    setFormComposerRenderingErrors,
  ] = React.useState(null);

  let initialConfigFormData = taskData.form;

  prepareRemoteProcedures(remoteProcedure);

  React.useEffect(() => {
    prepareFormData(
      taskData,
      setFormData,
      setLoadingFormData,
      setFormComposerRenderingErrors
    );
  }, [taskData.form]);

  if (!initialConfigFormData) {
    return <NoFormDataErrorsMessage />;
  }

  if (loadingFormData) {
    return <LoadingPresignedUrlsScreen />;
  }

  if (formComposerRenderingErrors) {
    return <RenderingErrorsMessage />;
  }

  return (
    <div>
      {formData && (
        <FormComposer
          data={formData}
          onSubmit={onSubmit}
          finalResults={finalResults}
          setRenderingErrors={setFormComposerRenderingErrors}
        />
      )}
    </div>
  );
}

export { LoadingScreen, FormComposerBaseFrontend };
