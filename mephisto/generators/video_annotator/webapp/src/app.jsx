/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { ErrorBoundary, useMephistoRemoteProcedureTask } from "mephisto-core";
import React from "react";
import ReactDOM from "react-dom";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import {
  LoadingScreen,
  VideoAnnotatorBaseFrontend,
} from "./components/core_components.jsx";

/* ================= Application Components ================= */

const STORAGE_USERNAME_KEY = "username";

function HomePage({
  handleFatalError,
  handleSubmit,
  initialTaskData,
  remoteProcedure,
}) {
  // In case of visiting home page but without any GET-parameters
  if (!initialTaskData?.annotator) {
    return (
      <div className={"container text-center mt-xl-5"}>
        <h2 className={"mb-xl-5"}>Welcome to Mephisto</h2>

        <div>
          <a href={"/welcome"}>Click here</a> to proceed to your tasks.
        </div>
      </div>
    );
  }

  // If all GET-parameters were passed and server returned task data
  return (
    <VideoAnnotatorBaseFrontend
      taskData={initialTaskData}
      onSubmit={handleSubmit}
      onError={handleFatalError}
      remoteProcedure={remoteProcedure}
    />
  );
}

function WelcomePage() {
  const storagedUsername = localStorage.getItem(STORAGE_USERNAME_KEY);

  const [username, setUsername] = React.useState(storagedUsername || "");

  function generateRandomString(len, chars) {
    chars =
      chars || "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    let randomString = "";
    for (let i = 0; i < len; i++) {
      let randomPoz = Math.floor(Math.random() * chars.length);
      randomString += chars.substring(randomPoz, randomPoz + 1);
    }
    return randomString;
  }

  function openTaskPage(e) {
    e.preventDefault();

    if (username === "") {
      alert("Username cannot be empty");
    } else {
      localStorage.setItem(STORAGE_USERNAME_KEY, username);
      window.location.replace(
        `/?worker_id=${username}&id=${generateRandomString(10)}`
      );
    }
  }

  return (
    <>
      <div className="card container mt-xl-5" style={{ width: "600px" }}>
        <div className="card-body">
          <h5 className="card-title text-center mb-xl-4">
            Welcome to Mephisto
          </h5>

          <form onSubmit={(e) => openTaskPage(e)}>
            <p className="card-text mb-xl-3">
              Please provide your username to start your task
            </p>

            <div className="form-group">
              <input
                className="form-control"
                id="id_username"
                placeholder={"Username"}
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>

            <button className={"btn btn-primary"} type={"submit"}>
              Start task
            </button>
          </form>
        </div>
      </div>
    </>
  );
}

function MainApp() {
  const {
    isLoading,
    initialTaskData,
    remoteProcedure,
    handleSubmit,
    handleFatalError,
  } = useMephistoRemoteProcedureTask();

  if (isLoading) {
    return <LoadingScreen />;
  }

  let _initialTaskData = initialTaskData;
  if (initialTaskData && initialTaskData.hasOwnProperty("task_data")) {
    _initialTaskData = initialTaskData.task_data;
  }

  return (
    <div>
      <ErrorBoundary handleError={handleFatalError}>
        <Routes>
          <Route path="/welcome" element={<WelcomePage />} />

          <Route
            path="/"
            element={
              <HomePage
                handleFatalError={handleFatalError}
                handleSubmit={handleSubmit}
                initialTaskData={_initialTaskData}
                remoteProcedure={remoteProcedure}
              />
            }
          />
        </Routes>
      </ErrorBoundary>
    </div>
  );
}

ReactDOM.render(
  <BrowserRouter>
    <MainApp />
  </BrowserRouter>,
  document.getElementById("app")
);
