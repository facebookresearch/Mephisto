/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import urls from "urls";
import generateURL from "./generateURL";
import makeRequest from "./makeRequest";

export function getTasks(
  setDataAction: SetRequestDataActionType,
  setLoadingAction: SetRequestLoadingActionType,
  setErrorsAction: SetRequestErrorsActionType,
  getParams: { [key: string]: string | number } = null,
  abortController?: AbortController
) {
  const url = generateURL(urls.server.tasks, null, getParams);

  makeRequest(
    "GET",
    url,
    null,
    (data) => setDataAction(data.tasks),
    setLoadingAction,
    setErrorsAction,
    "getTasks error:",
    abortController
  );
}

export function getTask(
  id: number,
  setDataAction: SetRequestDataActionType,
  setLoadingAction: SetRequestLoadingActionType,
  setErrorsAction: SetRequestErrorsActionType,
  abortController?: AbortController
) {
  const url = generateURL(urls.server.task, [id], null);

  makeRequest(
    "GET",
    url,
    null,
    (data) => setDataAction(data),
    setLoadingAction,
    setErrorsAction,
    "getTask error:",
    abortController
  );
}

export function getTaskWorkerUnitsIds(
  id: number,
  setDataAction: SetRequestDataActionType,
  setLoadingAction: SetRequestLoadingActionType,
  setErrorsAction: SetRequestErrorsActionType,
  getParams: { [key: string]: string | number } = null,
  abortController?: AbortController
) {
  const url = generateURL(urls.server.tasksWorkerUnitsIds, [id], getParams);

  makeRequest(
    "GET",
    url,
    null,
    (data) => setDataAction(data.worker_units_ids),
    setLoadingAction,
    setErrorsAction,
    "getTaskWorkerUnitsIds error:",
    abortController
  );
}

export function exportTaskResults(
  id: number,
  setDataAction: SetRequestDataActionType,
  setLoadingAction: SetRequestLoadingActionType,
  setErrorsAction: SetRequestErrorsActionType,
  abortController?: AbortController
) {
  const url = generateURL(urls.server.taskExportResults, [id]);

  makeRequest(
    "GET",
    url,
    null,
    setDataAction,
    setLoadingAction,
    setErrorsAction,
    "exportTaskResults error:",
    abortController
  );
}
