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
