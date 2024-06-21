/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import urls from "urls";
import generateURL from "./generateURL";
import makeRequest from "./makeRequest";

export function postWorkerBlock(
  id: string,
  setDataAction: SetRequestDataActionType,
  setLoadingAction: SetRequestLoadingActionType,
  setErrorsAction: SetRequestErrorsActionType,
  data: { [key: string]: string | number | string[] },
  abortController?: AbortController
) {
  const url = generateURL(urls.server.workersBlock, [id], null);

  makeRequest(
    "POST",
    url,
    JSON.stringify(data),
    (data) => setDataAction(data),
    setLoadingAction,
    setErrorsAction,
    "postWorkerBlock error:",
    abortController
  );
}

export function getWorkerGrantedQualifications(
  id: string,
  setDataAction: SetRequestDataActionType,
  setLoadingAction: SetRequestLoadingActionType,
  setErrorsAction: SetRequestErrorsActionType,
  abortController?: AbortController
) {
  const url = generateURL(urls.server.workerGrantedQualifications, [id]);

  makeRequest(
    "GET",
    url,
    null,
    (data) => setDataAction(data.granted_qualifications),
    setLoadingAction,
    setErrorsAction,
    "getWorkerGrantedQualifications error:",
    abortController
  );
}
