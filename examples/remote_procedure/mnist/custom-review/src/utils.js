/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import config from "./config";

function getHostname() {
  return config.port
    ? `${window.location.protocol}//${window.location.hostname}:${config.port}`
    : window.location.origin;
}

export { getHostname };
