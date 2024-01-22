/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import urls from "urls";
import generateURL from "./generateURL";
import makeRequest from "./makeRequest";

export function getStats(
  setDataAction: SetRequestDataActionType,
  setLoadingAction: SetRequestLoadingActionType,
  setErrorsAction: SetRequestErrorsActionType,
  getParams: { [key: string]: string | number } = null,
  abortController?: AbortController
) {
  const url = generateURL(urls.server.stats, null, getParams);

  makeRequest(
    "GET",
    url,
    null,
    (data) => setDataAction(data.stats),
    setLoadingAction,
    setErrorsAction,
    "getStats error:",
    abortController
  );
}
