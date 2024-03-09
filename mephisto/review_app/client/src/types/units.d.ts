/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

declare type UnitType = {
  id: number;
  worker_id: number | null;
  task_id: number | null;
  pay_amount: number;
  status: string;
  creation_date: string;
  results: {
    start: number;
    end: number;
    input_preview: null;
    output_preview: null;
  };
  review: {
    bonus: number | null;
    review_note: number | null;
  };
};

declare type WorkerUnitIdType = {
  unit_id: number;
  worker_id: number;
};

declare type UnitDetailsType = {
  has_task_source_review: boolean;
  id: number;
  inputs: object;
  outputs: object;
  prepared_inputs: object;
  unit_data_folder: string;
};
