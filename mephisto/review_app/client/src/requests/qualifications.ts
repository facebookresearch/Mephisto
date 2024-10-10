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
    "getQualifications error:",
    abortController
  );
}

export function getQualification(
  id: string,
  setDataAction: SetRequestDataActionType,
  setLoadingAction: SetRequestLoadingActionType,
  setErrorsAction: SetRequestErrorsActionType,
  abortController?: AbortController
) {
  const url = generateURL(urls.server.qualification, [id], null);

  makeRequest(
    "GET",
    url,
    null,
    (data) => setDataAction(data),
    setLoadingAction,
    setErrorsAction,
    "getQualification error:",
    abortController
  );
}

export function getQualificationDetails(
  id: string,
  setDataAction: SetRequestDataActionType,
  setLoadingAction: SetRequestLoadingActionType,
  setErrorsAction: SetRequestErrorsActionType,
  abortController?: AbortController
) {
  const url = generateURL(urls.server.qualificationDetails, [id], null);

  makeRequest(
    "GET",
    url,
    null,
    (data) => setDataAction(data),
    setLoadingAction,
    setErrorsAction,
    "getQualificationDetails error:",
    abortController
  );
}

export function getQualificationWorkers(
  id: string,
  setDataAction: SetRequestDataActionType,
  setLoadingAction: SetRequestLoadingActionType,
  setErrorsAction: SetRequestErrorsActionType,
  getParams: { [key: string]: string | number } = null,
  abortController?: AbortController
) {
  const url = generateURL(urls.server.qualificationWorkers, [id], getParams);

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

export function patchQualification(
  id: string,
  setDataAction: SetRequestDataActionType,
  setLoadingAction: SetRequestLoadingActionType,
  setErrorsAction: SetRequestErrorsActionType,
  data: { [key: string]: string | number },
  abortController?: AbortController
) {
  const url = generateURL(urls.server.qualification, [id], null);

  makeRequest(
    "PATCH",
    url,
    JSON.stringify(data),
    (data) => setDataAction(data),
    setLoadingAction,
    setErrorsAction,
    "patchQualification error:",
    abortController
  );
}

export function deleteQualification(
  id: string,
  setDataAction: SetRequestDataActionType,
  setLoadingAction: SetRequestLoadingActionType,
  setErrorsAction: SetRequestErrorsActionType,
  abortController?: AbortController
) {
  const url = generateURL(urls.server.qualification, [id], null);

  makeRequest(
    "DELETE",
    url,
    null,
    (data) => setDataAction(data),
    setLoadingAction,
    setErrorsAction,
    "deleteQualification error:",
    abortController
  );
}

export function postQualificationGrantWorker(
  qualificationId: string,
  workerId: string,
  setDataAction: SetRequestDataActionType,
  setLoadingAction: SetRequestLoadingActionType,
  setErrorsAction: SetRequestErrorsActionType,
  data: { [key: string]: string[] | number[] | number | string },
  abortController?: AbortController
) {
  const url = generateURL(
    urls.server.qualificationGrantWorker,
    [qualificationId, workerId],
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
  qualificationId: string,
  workerId: string,
  setDataAction: SetRequestDataActionType,
  setLoadingAction: SetRequestLoadingActionType,
  setErrorsAction: SetRequestErrorsActionType,
  data: { [key: string]: string[] | number[] | number | string },
  abortController?: AbortController
) {
  const url = generateURL(
    urls.server.qualificationRevokeWorker,
    [qualificationId, workerId],
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

export function patchQualificationGrantWorker(
  quailificationId: string,
  workerId: string,
  setDataAction: SetRequestDataActionType,
  setLoadingAction: SetRequestLoadingActionType,
  setErrorsAction: SetRequestErrorsActionType,
  data: { [key: string]: string[] | number[] | number | string },
  abortController?: AbortController
) {
  const url = generateURL(
    urls.server.qualificationGrantWorker,
    [quailificationId, workerId],
    null
  );

  makeRequest(
    "PATCH",
    url,
    JSON.stringify(data),
    (data) => setDataAction(data),
    setLoadingAction,
    setErrorsAction,
    "patchQualificationGrantWorker error:",
    abortController
  );
}

export function patchQualificationRevokeWorker(
  quailificationId: string,
  workerId: string,
  setDataAction: SetRequestDataActionType,
  setLoadingAction: SetRequestLoadingActionType,
  setErrorsAction: SetRequestErrorsActionType,
  abortController?: AbortController
) {
  const url = generateURL(
    urls.server.qualificationRevokeWorker,
    [quailificationId, workerId],
    null
  );

  makeRequest(
    "PATCH",
    url,
    "{}",
    (data) => setDataAction(data),
    setLoadingAction,
    setErrorsAction,
    "patchQualificationRevokeWorker error:",
    abortController
  );
}

export function getGrantedQualifications(
  setDataAction: SetRequestDataActionType,
  setLoadingAction: SetRequestLoadingActionType,
  setErrorsAction: SetRequestErrorsActionType,
  getParams: { [key: string]: string | number } = null,
  abortController?: AbortController
) {
  const url = generateURL(urls.server.grantedQualifications, null, getParams);

  makeRequest(
    "GET",
    url,
    null,
    (data) => setDataAction(data.granted_qualifications),
    setLoadingAction,
    setErrorsAction,
    "getGrantedQualifications error:",
    abortController
  );
}
