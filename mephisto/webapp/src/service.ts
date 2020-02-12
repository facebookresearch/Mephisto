import axios from "./axios";

export function launchTask(data: any) {
  const transformedPayload = mapDataToExpectedPayload(data);
  axios.post("task_runs/launch", transformedPayload);
}

function mapDataToExpectedPayload(data: any) {
  const transformed = Object.entries(data).map(([key, value]) => {
    if (key === "blueprint") {
      return [
        "blueprint_type",
        {
          option_string: "--blueprint_type",
          value: value
        }
      ];
    } else if (key === "architect") {
      return [
        "architect_type",
        {
          option_string: "--architect_type",
          value: value
        }
      ];
    } else {
      const [namespace, arg_name, opt_string] = key.split("|");
      return [arg_name, { option_string: opt_string, value: value }];
    }
  });

  return Object.fromEntries(transformed);
}
