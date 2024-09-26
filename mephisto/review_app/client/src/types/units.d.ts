/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

declare type UnitType = {
  created_at: string;
  id: string;
  is_reviewed: boolean;
  pay_amount: number;
  results: {
    start: number;
    end: number;
    inputs_preview: null;
    outputs_preview: null;
  };
  review: {
    bonus: number | null;
    review_note: number | null;
  };
  status: string;
  task_id: string | null;
  worker_id: string | null;
};

declare type WorkerUnitIdType = {
  unit_id: string;
  worker_id: string;
};

declare type WorkerOpinionAttachmentType = {
  destination: string;
  encoding: string;
  fieldname: string;
  filename: string;
  mimetype: string;
  originalname: string;
  path: string;
  size: number;
};

declare type WorkerOpinionQuestionType = {
  answer: string;
  question: string;
  reviewed: boolean;
  toxicity: any;
};

declare type WorkerOpinionType = {
  attachments: WorkerOpinionAttachmentType[];
  questions: WorkerOpinionQuestionType[];
};

declare type UnitDetailsMetadataType = {
  worker_opinion?: WorkerOpinionType;
  webvtt?: string;
};

declare type UnitDetailsType = {
  has_task_source_review: boolean;
  id: string;
  inputs: object;
  metadata: UnitDetailsMetadataType;
  outputs: object;
  prepared_inputs: object;
  unit_data_folder: string;
};
