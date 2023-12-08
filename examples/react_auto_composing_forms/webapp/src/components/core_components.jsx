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

function AutoComposingFormFrontend({ taskData, onSubmit, onError, finalResults = null }) {
  let formData = taskData.form;

  if (!formData) {
    return (
      <div>
        Passed form data is invalid... Recheck your task config.
      </div>
    );
  }

  // const _finalResults = {
  //   "name_first": "Saved name first",
  //   "name_last": "Saved name last",
  //   "email": "saved@example.com",
  //   "country": "CAN",
  //   "language": ["fr", "es"],
  //   "bio": "Some bio text about me",
  //   "skills": {
  //     "javascript": true,
  //     "python": true,
  //     "react": false,
  //   },
  //   "kids": ">=3",
  //   // "avatar": "/path/to/file.jpg",
  // }

  return (
    <div>
      <FormComposer
        data={formData}
        onSubmit={onSubmit}
        finalResults={finalResults}
      />
    </div>
  );
}

export { LoadingScreen, AutoComposingFormFrontend };
