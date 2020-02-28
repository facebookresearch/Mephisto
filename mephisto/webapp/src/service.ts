import axios from "./axios";
import { AxiosPromise } from "axios";

export function launchTask(data: any): AxiosPromise<any> {
  const transformedPayload = mapDataToExpectedPayload(data);
  return axios.post("task_runs/launch", transformedPayload);
}

function mapDataToExpectedPayload(data: any) {
  // We expect to receive a payload of the following format that
  // will then transform to suit the API's expectations:
  //
  // {
  //    "blueprint": "name",
  //    "architect": "name",
  //    "requester": "name",
  //    "bp|<arg-name>|<--arg-flag>": "value"
  // }
  const transformed = Object.entries(data).map(([key, value]) => {
    if (key === "blueprint") {
      return [
        "blueprint_type",
        {
          option_string: "--blueprint-type",
          value: value
        }
      ];
    } else if (key === "architect") {
      return [
        "architect_type",
        {
          option_string: "--architect-type",
          value: value
        }
      ];
    } else if (key === "requester") {
      return [
        "requester_name",
        {
          option_string: "--requester-name",
          value: value
        }
      ];
    } else {
      const [namespace, arg_name, opt_string] = key.split("|");
      return [
        arg_name,
        {
          option_string: opt_string,
          value: value === null ? null : (value as any).toString()
        }
      ];
    }
  });

  console.table(Object.fromEntries(transformed));
  return Object.fromEntries(transformed);
}
