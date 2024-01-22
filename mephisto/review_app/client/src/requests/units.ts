/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import urls from "urls";
import generateURL from "./generateURL";
import makeRequest from "./makeRequest";

export function getUnits(
  setDataAction: SetRequestDataActionType,
  setLoadingAction: SetRequestLoadingActionType,
  setErrorsAction: SetRequestErrorsActionType,
  getParams: { [key: string]: string | number } = null,
  abortController?: AbortController
) {
  const url = generateURL(urls.server.units, null, getParams);

  makeRequest(
    "GET",
    url,
    null,
    (data) => setDataAction(data.units),
    setLoadingAction,
    setErrorsAction,
    "getUnits error:",
    abortController
  );
}

export function getUnitsDetails(
  setDataAction: SetRequestDataActionType,
  setLoadingAction: SetRequestLoadingActionType,
  setErrorsAction: SetRequestErrorsActionType,
  getParams: { [key: string]: string | number } = null,
  abortController?: AbortController
) {
  const url = generateURL(urls.server.unitsDetails, null, getParams);

  makeRequest(
    "GET",
    url,
    null,
    (data) => setDataAction(data.units),
    setLoadingAction,
    setErrorsAction,
    "getUnitsDetails error:",
    abortController
  );
}

export function postUnitsApprove(
  setDataAction: SetRequestDataActionType,
  setLoadingAction: SetRequestLoadingActionType,
  setErrorsAction: SetRequestErrorsActionType,
  data: { [key: string]: number[] | string | number | boolean },
  abortController?: AbortController
) {
  const url = generateURL(urls.server.unitsApprove, null, null);

  makeRequest(
    "POST",
    url,
    JSON.stringify(data),
    (data) => setDataAction(data),
    setLoadingAction,
    setErrorsAction,
    "postUnitsApprove error:",
    abortController
  );
}

export function postUnitsReject(
  setDataAction: SetRequestDataActionType,
  setLoadingAction: SetRequestLoadingActionType,
  setErrorsAction: SetRequestErrorsActionType,
  data: { [key: string]: number[] | string | boolean },
  abortController?: AbortController
) {
  const url = generateURL(urls.server.unitsReject, null, null);

  makeRequest(
    "POST",
    url,
    JSON.stringify(data),
    (data) => setDataAction(data),
    setLoadingAction,
    setErrorsAction,
    "postUnitsReject error:",
    abortController
  );
}

export function postUnitsSoftReject(
  setDataAction: SetRequestDataActionType,
  setLoadingAction: SetRequestLoadingActionType,
  setErrorsAction: SetRequestErrorsActionType,
  data: { [key: string]: number[] | string | boolean },
  abortController?: AbortController
) {
  const url = generateURL(urls.server.unitsSoftReject, null, null);

  makeRequest(
    "POST",
    url,
    JSON.stringify(data),
    (data) => setDataAction(data),
    setLoadingAction,
    setErrorsAction,
    "postUnitsSoftReject error:",
    abortController
  );
}
