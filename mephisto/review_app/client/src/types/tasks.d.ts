/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

declare type TaskType = {
  created_at: string;
  has_stats: boolean;
  id: string;
  is_reviewed: boolean;
  name: string;
  unit_count: number;
};

declare type TaskStatsType = {
  approved_count: number;
  rejected_count: number;
  reviewed_count: number;
  soft_rejected_count: number;
  total_count: number;
};

declare type TaskRusultStatsType = {
  stats: { [key: string]: { [key: string]: number } };
  task_id: string;
  task_name: string;
  workers_count: number;
};
