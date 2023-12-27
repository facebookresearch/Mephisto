/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

type FormType = {
  bonus: number | null;
  checkboxAssignQualification?: boolean;
  checkboxBanWorker?: boolean;
  checkboxGiveBonus?: boolean;
  checkboxReviewNote: boolean;
  checkboxReviewNoteSend?: boolean;
  checkboxUnassignQualification?: boolean;
  newQualificationValue?: string;
  qualification: number | null;
  qualificationValue: number;
  reviewNote: string;
  showNewQualification?: boolean;
};

type ModalDataType = {
  applyToNext: boolean;
  applyToNextUnitsCount: number;
  buttonCancel: string;
  buttonSubmit: string;
  form: FormType;
  title: string;
  type: string;
};

type ModalStateType = {
  approve: {
    applyToNext: boolean;
    form: FormType;
  };
  softReject: {
    applyToNext: boolean;
    form: FormType;
  };
  reject: {
    applyToNext: boolean;
    form: FormType;
  };
};
