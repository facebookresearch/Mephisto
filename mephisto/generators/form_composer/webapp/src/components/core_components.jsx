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
} from "react-form-composer";

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
    <section className="hero is-light" data-cy="directions-container">
      <div className="hero-body">
        <div className="container">
          <p className="subtitle is-5">{children}</p>
        </div>
      </div>
    </section>
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

  const inReviewState = finalResults !== null;
  const initialConfigFormData = taskData.form;

  if (!inReviewState) {
    prepareRemoteProcedures(remoteProcedure);
  }

  React.useEffect(() => {
    if (inReviewState) {
      setFormData(initialConfigFormData);
    } else {
      prepareFormData(
        taskData,
        setFormData,
        setLoadingFormData,
        setFormComposerRenderingErrors
      );
    }
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
