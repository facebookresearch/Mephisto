/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { configure } from "axios-hooks";
import Axios, { AxiosRequestConfig } from "axios";

const axios = Axios.create({
  baseURL: "http://localhost:5000/api/v1/",
});

declare module "axios" {
  export interface AxiosRequestConfig {
    delayed?: boolean | number;
  }
}

// type CustomAxiosRequestConfig = AxiosRequestConfig & { delayed?: boolean };

axios.interceptors.request.use((config) => {
  if (config.delayed) {
    return new Promise((resolve) =>
      setTimeout(
        () => resolve(config),
        config.delayed === true
          ? 600
          : config.delayed === false
          ? 0
          : config.delayed
      )
    );
  }
  return config;
});

configure({ axios });

export default axios;
