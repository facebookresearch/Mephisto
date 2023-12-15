/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import cloneDeep from "lodash/cloneDeep";

export const updateModalState = (
  setStateFunc: Function,
  type: string,
  formData: ModalDataType
) => {
  setStateFunc((stateValue: ModalStateType) => {
    const newValue = cloneDeep(stateValue[type]);

    newValue.applyToNext = formData.applyToNext;
    newValue.form = formData.form;

    stateValue[type] = newValue;

    return stateValue;
  });
};

export function setPageTitle(title: string) {
  const titleElement = document.querySelector("title");
  titleElement.innerText = title;
}
