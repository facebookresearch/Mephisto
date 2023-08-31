/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min';
import HomePage from 'pages/HomePage/HomePage';
import QualificationsPage from 'pages/QualificationsPage/QualificationsPage';
import TaskPage from 'pages/TaskPage/TaskPage';
import TasksPage from 'pages/TasksPage/TasksPage';
import * as React from 'react';
import { Route, Routes } from 'react-router-dom';
import urls from 'urls';
import css from './App.css';


function App() {
  return (
    <div className={css.app}>
      <Routes>
        <Route path={urls.client.home} element={<HomePage />} />
        <Route path={urls.client.task(':id')} element={<TaskPage />} />
        <Route path={urls.client.tasks} element={<TasksPage />} />
        <Route path={urls.client.qualifications} element={<QualificationsPage />} />
      </Routes>
    </div>
  );
}


export default App;
