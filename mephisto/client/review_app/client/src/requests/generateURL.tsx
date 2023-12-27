/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

const generateURL = (
  path: string | Function,
  pathParams: Array<string | number> = null,
  getParams: { [key: string]: string | number } = null
): string => {
  pathParams = pathParams || [];

  if (typeof path === "function") {
    path = path(...pathParams) as string;
  }

  if (getParams) {
    const paramsString = Object.keys(getParams)
      .map((key) => {
        return key + "=" + encodeURIComponent(String(getParams[key]));
      })
      .join("&") as string;

    path += "?" + paramsString;
  }

  return path;
};

export default generateURL;
