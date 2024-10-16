/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

declare type QualificationType = {
  creation_date: string;
  description: string;
  id: string;
  name: string;
};

declare type QualificationDetailsType = {
  granted_qualifications_count: number;
};

declare type GrantedQualificationType = {
  granted_at: string;
  qualification_id: number;
  value: number;
  worker_id: string;
};

declare type WorkerGrantedQualificationsType = {
  [key: string]: GrantedQualificationType;
};

declare type SelectedQualificationType = {
  qualification_id: string;
  qualification_name: string;
  value: number;
};

declare type SelectedQualificationsType = {
  [key: string]: SelectedQualificationType;
};

declare type FGQUnit = {
  creation_date: string;
  task_id: string;
  task_name: string;
  unit_id: string;
  value: string;
};

declare type FullGrantedQualificationType = {
  granted_at: string;
  qualification_id: string;
  qualification_name: string;
  units: FGQUnit[];
  value_current: number;
  worker_id: string;
  worker_name: string;
};

declare type CreateQualificationFormType = {
  description: string;
  name: string;
};
