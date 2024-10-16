/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { SortArrowsState } from "components/ColumnTitleWithSort/ColumnTitleWithSort";
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

export function capitalizeString(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

export function setResponseErrors(
  setErrorsFunc: Function,
  errorResponse: ErrorResponseType | null
) {
  if (errorResponse) {
    setErrorsFunc((oldErrors) => [...oldErrors, ...[errorResponse.error]]);
  }
}

export function onClickSortTableColumn(
  columnName: string,
  state: SortArrowsState,
  onChangeSortParamFunc: Function,
  setCurrentSortFunc: Function
) {
  let _sortParam = "";
  if (state === SortArrowsState.INACTIVE) {
    _sortParam = "";
  } else if (state === SortArrowsState.ASC) {
    _sortParam = columnName;
  } else if (state === SortArrowsState.DESC) {
    _sortParam = `-${columnName}`;
  } else {
  }

  onChangeSortParamFunc(_sortParam);
  setCurrentSortFunc({ column: columnName, state: state });
}
