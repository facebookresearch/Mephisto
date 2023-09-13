/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { ReviewType } from 'consts/review';


export const APPROVE_MODAL_DATA_STATE: ModalDataType = {
  applyToNext: false,
  buttonCancel: "Cancel",
  buttonSubmit: "Approve",
  form: {
    checkboxAssign: false,
    checkboxComment: false,
    checkboxGiveTips: false,
    comment: '',
    qualification: null,
    qualificationValue: 1,
    tips: null,
  },
  title: "Approve Item",
  type: ReviewType.APPROVE,
};


export const SOFT_REJECT_MODAL_DATA_STATE: ModalDataType = {
  applyToNext: false,
  buttonCancel: "Cancel",
  buttonSubmit: "Soft-Reject",
  form: {
    checkboxAssign: false,
    checkboxComment: false,
    checkboxGiveTips: false,
    comment: '',
    qualification: null,
    qualificationValue: 1,
    tips: null,
  },
  title: "Soft-Reject Item",
  type: ReviewType.SOFT_REJECT,
};


export const REJECT_MODAL_DATA_STATE: ModalDataType = {
  applyToNext: false,
  buttonCancel: "Cancel",
  buttonSubmit: "Reject",
  title: "Reject Item",
  type: ReviewType.REJECT,
  form: {
    checkboxAssign: false,
    checkboxComment: false,
    checkboxBanWorker: false,
    comment: '',
    qualification: null,
    qualificationValue: 1,
    tips: null,
  }
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
