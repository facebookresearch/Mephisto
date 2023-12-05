/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import { FormComposer } from './FormComposer/FormComposer';

function LoadingScreen() {
  return <Directions>Loading...</Directions>;
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

function AutoComposingFormFrontend({ taskData, onSubmit, onError }) {
  let formData = taskData.form;

  if (!formData) {
    return (
      <div>
        Passed form data is invalid... Recheck your task config.
      </div>
    );
  }

  return (
    <div>
      <FormComposer data={formData} onSubmit={onSubmit} />
    </div>
  );
}

export { LoadingScreen, AutoComposingFormFrontend };
