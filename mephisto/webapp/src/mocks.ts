/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
import { TaskRun, RunningTasks } from "./models";

export const task_runs__running: RunningTasks = {
  live_task_count: 1,
  task_count: 1,
  task_runs: [
    {
      param_string:
        "--test --task --run --test --task --run --test --task --run --test --task --run --test --task --run --test --task --run --test --task --run --test --task --run --test --task --run ",
      params: {
        "run params": "Coming soon!",
        status: "Not yet implemented",
      },
      sandbox: false,
      start_time: "2019-12-09 22:53:30",
      task_id: "1",
      task_name: "test_task",
      task_run_id: "1",
      task_status: {
        accepted: 0,
        assigned: 0,
        completed: 0,
        created: 3,
        expired: 0,
        launched: 0,
        mixed: 0,
        rejected: 0,
      },
      task_type: "mock",
    },
  ],
};
