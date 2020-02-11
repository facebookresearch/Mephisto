import axios from "./axios";

export function launchTask(data: any) {
  axios.post("launch_task_run", data);
}
