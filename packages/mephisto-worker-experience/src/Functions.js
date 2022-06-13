/**
 * @callback submitCallback
 * @callback changeCallback
 */

/**
 * Creates a tip in the format that is accepted
 * by the handleMetadataSubmit function from the
 * mephisto-task library
 * @param {string} header
 * @param {string} text
 * @returns {{ header: string; text: string; type: string; }} A tips obj for handleMetadataSubmit()
 */
export function createTip(header, text) {
  if (!header || !typeof header === "string" || !header instanceof String) {
    return new Promise(function (resolve, reject) {
      reject("Tip header is not a string");
    });
  }
  if (!text || !typeof text === "string" || !text instanceof String) {
    return new Promise(function (resolve, reject) {
      reject("Tip text is not a string");
    });
  }
  return {
    header: header,
    text: text,
    type: "tips",
  };
}

/**
 * Creates a feedback item in the format that is accepted
 * by the handleMetadataSubmit function from the
 * mephisto-task library
 * @param {string} text
 * @returns {{ text: string; type: "string"; }} A feedback obj for handleMetadataSubmit()
 */
export function createFeedback(text) {
  if (!text || !typeof text === "string" || !text instanceof String) {
    return new Promise(function (resolve, reject) {
      reject("Feedback text is not a string");
    });
  }
  return {
    text: text,
    type: "feedback",
  };
}
const hideAlertDelay = 5000;

/** When handleSubmit is not defined, this
 * function submits the current tip data to the backend.
 * It also does success/error handling.
 *
 * When handleSubmit is defined, the handleSubmit
 * function is ran with the tipData obj as its first parameter.
 *
 * @param {submitCallback} handleSubmit
 * @param {submitCallback} handleMetadataSubmit
 * @param {React.Dispatch<any>} dispatch
 * @param {{ header: string; text: string; }} tipData
 * @param {React.Dispatch<React.SetStateAction<{ header: string; text: string; }>>} setTipData
 * @return
 */
export function handleTipSubmit(
  handleSubmit,
  handleMetadataSubmit,
  dispatch,
  tipData,
  setTipData
) {
  if (handleSubmit) handleSubmit(tipData);
  else {
    dispatch({ type: "loading" });
    handleMetadataSubmit(createTip(tipData.header, tipData.text))
      .then((data) => {
        if (data.status === "Submitted metadata for review") {
          setTipData({ header: "", text: "" });
          dispatch({ type: "success" });
          setTimeout(() => {
            dispatch({ type: "return-to-default" });
          }, hideAlertDelay);
        }
      })
      .catch((error) => {
        console.error(error);
        dispatch({ type: "error" });
        setTimeout(() => {
          dispatch({ type: "return-to-default" });
        }, hideAlertDelay);
      });
  }
}

/** When handleSubmit is not defined, this
 * function submits the current feedback data to the backend.
 * It also does success/error handling.
 *
 * When handleSubmit is defined, the handleSubmit
 * function is ran with the feedbackData obj as its first parameter.
 *
 * @param {submitCallback} handleSubmit
 * @param {submitCallback} handleMetadataSubmit
 * @param {React.Dispatch<any>} dispatch
 * @param {string} feedbackText
 * @param {React.Dispatch<React.SetStateAction<string>>} setFeedbackText
 * @return
 */
export function handleFeedbackSubmit(
  handleSubmit,
  handleMetadataSubmit,
  dispatch,
  feedbackText,
  setFeedbackText
) {
  if (handleSubmit) handleSubmit(feedbackText);
  else {
    dispatch({ type: "loading" });
    handleMetadataSubmit(createFeedback(feedbackText))
      .then((data) => {
        if (data.status === "Submitted metadata for review") {
          setFeedbackText("");
          dispatch({ type: "success" });
          setTimeout(() => {
            dispatch({ type: "return-to-default" });
          }, hideAlertDelay);
        }
      })
      .catch((error) => {
        console.error(error);
        dispatch({ type: "error" });
        setTimeout(() => {
          dispatch({ type: "return-to-default" });
        }, hideAlertDelay);
      });
  }
}

/**
 * Runs the change callback when typing occurs in an input.
 * If the input content is too long, then change state
 * @param {React.ChangeEvent<HTMLInputElement>} e A typical react event
 * @param {any} state State that is retrived from reducer. It should have a status property.
 * @param {React.Dispatch<any>} dispatch Dispatch that is retrieved from reducer
 * @param {changeCallback} changeCallback A function that gets ran on every keystroke
 * @param {int} maxLength The largest length before an error message will show
 * @return
 */
export function handleChangeFeedback(e, state, dispatch, changeCallback, maxLength) {
  changeCallback(e);
  if (e.target.value.length > maxLength && state.status !== 4) {
    dispatch({ type: "too-long" });
  } else if (e.target.value.length <= maxLength) {
    dispatch({ type: "return-to-default" });
  }
}
