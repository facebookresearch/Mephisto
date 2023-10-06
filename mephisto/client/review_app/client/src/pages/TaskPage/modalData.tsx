/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { ReviewType } from "consts/review";

export const APPROVE_MODAL_DATA_STATE: ModalDataType = {
  applyToNext: false,
  applyToNextUnitsCount: 0,
  buttonCancel: "Cancel",
  buttonSubmit: "Approve",
  form: {
    checkboxAssignQualification: false,
    checkboxReviewNote: false,
    checkboxGiveBonus: false,
    reviewNote: "",
    qualification: null,
    qualificationValue: 1,
    bonus: null,
  },
  title: "Approve Unit",
  type: ReviewType.APPROVE,
};

export const SOFT_REJECT_MODAL_DATA_STATE: ModalDataType = {
  applyToNext: false,
  applyToNextUnitsCount: 0,
  buttonCancel: "Cancel",
  buttonSubmit: "Soft-Reject",
  form: {
    checkboxAssignQualification: false,
    checkboxReviewNote: false,
    reviewNote: "",
    qualification: null,
    qualificationValue: 1,
    bonus: null,
  },
  title: "Soft-Reject Unit",
  type: ReviewType.SOFT_REJECT,
};

export const REJECT_MODAL_DATA_STATE: ModalDataType = {
  applyToNext: false,
  applyToNextUnitsCount: 0,
  buttonCancel: "Cancel",
  buttonSubmit: "Reject",
  title: "Reject Unit",
  type: ReviewType.REJECT,
  form: {
    checkboxUnassignQualification: false,
    checkboxReviewNote: false,
    checkboxBanWorker: false,
    reviewNote: "",
    qualification: null,
    qualificationValue: 1,
    bonus: null,
  },
};

export const DEFAULT_MODAL_STATE_VALUE: ModalStateType = {
  approve: {
    applyToNext: false,
    form: APPROVE_MODAL_DATA_STATE.form,
  },
  softReject: {
    applyToNext: false,
    form: SOFT_REJECT_MODAL_DATA_STATE.form,
  },
  reject: {
    applyToNext: false,
    form: REJECT_MODAL_DATA_STATE.form,
  },
};
