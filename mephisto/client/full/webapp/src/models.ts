/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
export interface Requester {
  provider_type: string;
  registered: boolean;
  requester_id: string;
  requester_name: string;
}

export interface Requesters {
  requesters: Requester[];
}

export interface LaunchOptions {
  architect_types: string[];
  blueprint_types: { name: string; rank: number }[];
  provider_types: string[];
  success: boolean;
}

export interface ParamDetails {
  choices: string[] | null;
  default: string;
  dest: string;
  help: string;
  option_string: string;
  type: string;
}

export type Provider = string;

export interface TaskRun {
  param_string: string; // "--test --task --run"
  params: object; // { "run params": "Coming soon!"; status: "Not yet implemented"; }
  sandbox: boolean;
  start_time: string; // "2019-12-09 22:53:30"
  task_id: string; // "1"
  task_name: string; // "test_task"
  task_run_id: string; // "1"
  task_status: {
    accepted: number;
    assigned: number;
    completed: number;
    created: number;
    expired: number;
    launched: number;
    mixed: number;
    rejected: number;
  };
  task_type: string; // "mock" (it's the blueprint name)
}

export interface RunningTasks {
  live_task_count: number;
  task_count: number;
  task_runs: TaskRun[];
}

export interface ReviewableTasks {
  task_runs: TaskRun[];
  total_reviewable: number;
}
