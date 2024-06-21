/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

declare type QualificationType = {
  id: string;
  name: string;
};

declare type GrantedQualificationType = {
  worker_id: string;
  qualification_id: number;
  value: number;
  granted_at: string;
};

declare type WorkerGrantedQualificationsType = {
  [key: string]: GrantedQualificationType;
};
