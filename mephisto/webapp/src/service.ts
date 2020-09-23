/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
import axios from "./axios";
import { AxiosPromise } from "axios";

// TEMP HACK NULL_FIELDS: some static task fields have a default value of null
// while null is also an unacceptable value, we detect explict exceptions for now
// and handle the process of skipping these fields
const SKIP_FIELD = null;

export function launchTask(data: any): AxiosPromise<any> {
  const transformedPayload = mapLaunchDataToExpectedPayload(data);
  return axios.post("task_runs/launch", transformedPayload);
}

export function createRequester(
  provider: string,
  payload: any
): AxiosPromise<any> {
  return axios.post(`requester/${provider}/register`, payload);
}

function mapLaunchDataToExpectedPayload(data: any) {
  // We expect to receive a payload of the following format that
  // will then transform to suit the API's expectations:
  //
  // {
  //    "blueprint": "name",
  //    "architect": "name",
  //    "requester": "name",
  //    "bp|<arg-name>|<--arg-flag>": "value"
  // }
  const transformed = Object.entries(data)
    .map(([key, value]) => {
      if (key === "blueprint") {
        return [
          "blueprint_type",
          {
            option_string: "--blueprint-type",
            value: value,
          },
        ];
      } else if (key === "architect") {
        return [
          "architect_type",
          {
            option_string: "--architect-type",
            value: value,
          },
        ];
      } else if (key === "requester") {
        return [
          "requester_name",
          {
            option_string: "--requester-name",
            value: value,
          },
        ];
      } else {
        const [namespace, arg_name, opt_string] = key.split("|");

        /* TEMP HACK NULL_FIELDS - handle in a more sophisticated fashion once optional or required flags are added */
        if (namespace === "bp" && value === null) {
          return [SKIP_FIELD, SKIP_FIELD];
        }

        return [
          arg_name,
          {
            option_string: opt_string,
            value: value === null ? null : (value as any).toString(),
          },
        ];
      }
    })
    .filter(([arg, data]) => arg !== SKIP_FIELD);
  /* ^ TEMP HACK NULL_FIELDS filter out empty fields */

  console.table(Object.fromEntries(transformed));
  return Object.fromEntries(transformed);
}

export const reviewActions = {
  accept: function (id: string) {
    return axios.post(`unit/${id}/accept`);
  },
  rejectAndPay: function (id: number) {
    return axios.post(`unit/${id}/reject`);
  },
  softBlock: function (id: number) {
    return axios.post(`unit/${id}/softBlock`);
  },
  hardBlock: function (id: number) {
    return axios.post(`unit/${id}/hardBlock`);
  },
};
