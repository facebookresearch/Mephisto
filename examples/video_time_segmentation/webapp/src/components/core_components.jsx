/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";

function OnboardingComponent({ onSubmit }) {
  return (
    <div>
      <Directions>
        This component only renders if you have chosen to assign an onboarding
        qualification for your task. Click the button to move on to the main
        task.
      </Directions>
      <button
        className="button is-link"
        onClick={() => onSubmit({ success: true })}
      >
        Move to main task.
      </button>
    </div>
  );
}

function LoadingScreen() {
  return <Directions>Loading...</Directions>;
}

function Directions({ children }) {
  return (
    <section class="hero is-light">
      <div class="hero-body">
        <div class="container">
          <p class="subtitle is-5">{children}</p>
        </div>
      </div>
    </section>
  );
}

function SimpleFrontend({ taskData, isOnboarding, onSubmit }) {
  if (!taskData) {
    return <LoadingScreen />;
  }
  if (isOnboarding) {
    return <OnboardingComponent onSubmit={onSubmit} />;
  }
  console.log(taskData);
  console.table(taskData);
  return (
    <div>
      <Directions>
        Directions: The task data is listed in the console logs
      </Directions>
    </div>
  );
}

export { LoadingScreen, SimpleFrontend as BaseFrontend };
