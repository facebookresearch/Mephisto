/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

type FormType = {
  checkboxAssign: boolean;
  checkboxBanWorker?: boolean;
  checkboxComment: boolean;
  checkboxGiveTips?: boolean;
  comment: string;
  qualification: number | null;
  qualificationValue: number;
  tips: number | null;
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
