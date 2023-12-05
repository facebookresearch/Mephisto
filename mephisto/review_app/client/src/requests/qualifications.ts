/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import urls from "urls";
import generateURL from "./generateURL";
import makeRequest from "./makeRequest";

export function getQualifications(
  setDataAction: SetRequestDataActionType,
  setLoadingAction: SetRequestLoadingActionType,
  setErrorsAction: SetRequestErrorsActionType,
  getParams: { [key: string]: string | number } = null,
  abortController?: AbortController
) {
  const url = generateURL(urls.server.qualifications, null, getParams);

  makeRequest(
    "GET",
    url,
    null,
    (data) => setDataAction(data.qualifications),
    setLoadingAction,
    setErrorsAction,
    "getTasks error:",
    abortController
  );
}

export function getQualificationWorkers(
  id: number,
  setDataAction: SetRequestDataActionType,
  setLoadingAction: SetRequestLoadingActionType,
  setErrorsAction: SetRequestErrorsActionType,
  getParams: { [key: string]: string | number } = null,
  abortController?: AbortController
) {
  const url = generateURL(
    urls.server.qualificationWorkers(id),
    null,
    getParams
  );

  makeRequest(
    "GET",
    url,
    null,
    (data) => setDataAction(data.workers),
    setLoadingAction,
    setErrorsAction,
    "getQualificationWorkers error:",
    abortController
  );
}

export function postQualification(
  setDataAction: SetRequestDataActionType,
  setLoadingAction: SetRequestLoadingActionType,
  setErrorsAction: SetRequestErrorsActionType,
  data: { [key: string]: string | number },
  abortController?: AbortController
) {
  const url = generateURL(urls.server.qualifications, null, null);

  makeRequest(
    "POST",
    url,
    JSON.stringify(data),
    (data) => setDataAction(data),
    setLoadingAction,
    setErrorsAction,
    "postQualification error:",
    abortController
  );
}

export function postQualificationGrantWorker(
  id: number,
  workerId: number,
  setDataAction: SetRequestDataActionType,
  setLoadingAction: SetRequestLoadingActionType,
  setErrorsAction: SetRequestErrorsActionType,
  data: { [key: string]: string[] | number[] | number | string },
  abortController?: AbortController
) {
  const url = generateURL(
    urls.server.qualificationGrantWorker(id, workerId),
    null,
    null
  );

  makeRequest(
    "POST",
    url,
    JSON.stringify(data),
    (data) => setDataAction(data),
    setLoadingAction,
    setErrorsAction,
    "postQualificationGrantWorker error:",
    abortController
  );
}

export function postQualificationRevokeWorker(
  id: number,
  workerId: number,
  setDataAction: SetRequestDataActionType,
  setLoadingAction: SetRequestLoadingActionType,
  setErrorsAction: SetRequestErrorsActionType,
  data: { [key: string]: string[] | number[] | number | string },
  abortController?: AbortController
) {
  const url = generateURL(
    urls.server.qualificationRevokeWorker(id, workerId),
    null,
    null
  );

  makeRequest(
    "POST",
    url,
    JSON.stringify(data),
    (data) => setDataAction(data),
    setLoadingAction,
    setErrorsAction,
    "postQualificationRevokeWorker error:",
    abortController
  );
}
