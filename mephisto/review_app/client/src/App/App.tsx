/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.bundle.min";
import Errors from "components/Errors/Errors";
import HomePage from "pages/HomePage/HomePage";
import TaskPage from "pages/TaskPage/TaskPage";
import TasksPage from "pages/TasksPage/TasksPage";
import * as React from "react";
import { Route, Routes } from "react-router-dom";
import urls from "urls";
import css from "./App.css";

function App() {
  const [errors, setErrors] = React.useState<string[]>([]);

  return (
    <div className={css.app}>
      <Routes>
        <Route
          path={urls.client.home}
          element={<HomePage setErrors={setErrors} />}
        />
        <Route
          path={urls.client.task(":id")}
          element={<TaskPage setErrors={setErrors} />}
        />
        <Route
          path={urls.client.tasks}
          element={<TasksPage setErrors={setErrors} />}
        />
      </Routes>

      <Errors errorList={errors} />
    </div>
  );
}

export default App;
