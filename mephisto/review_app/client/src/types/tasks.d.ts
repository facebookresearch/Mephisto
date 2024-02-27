/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

declare type TaskType = {
  id: number;
  name: string;
  is_reviewed: boolean;
  unit_count: number;
  created_at: string;
};

declare type TaskStatsType = {
  total_count: number;
  reviewed_count: number;
  approved_count: number;
  rejected_count: number;
  soft_rejected_count: number;
};
