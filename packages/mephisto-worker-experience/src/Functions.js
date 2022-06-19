/**
 * @callback submitCallback
 * @callback changeCallback
 */

/**
 * Creates a tip in the format that is accepted
 * by the handleMetadataSubmit function from the
 * mephisto-task library
 * @param {string} header The tip header
 * @param {string} text The tip text or a.k.a the tip body
 * @return {{header: string; text: string; type: string; }} An object that can be used as a parameter of
 *                                                          the handleSubmitMetadata() method in the mephisto-task package
 */
export function createTip(header, text) {
  if (!header || !(typeof header === "string"))
    throw new Error("Tip header is not a string");

  if (!text || !(typeof text === "string"))
    throw new Error("Tip text is not a string");

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
 * @param {string} text The feedback text
 * @return {{text: text; type: "feedback"; }} An object that can be used as a parameter of the
 *                                            handleSubmitMetadata() method in the mephisto-task package
 */
export function createFeedback(text) {
  if (!text || !(typeof text === "string") || !(text instanceof String))
    throw new Error("Feedback text is not a string");

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
 * Runs the change callback when typing occurs in a tip text input.
 * If the tip text area input is too long, then change state
 * @param {React.ChangeEvent<HTMLInputElement>} e A typical react event
 * @param {header: string; text: string} tipData Stores data for the tip
 * @param {any} state State that is retrived from reducer. It should have a status property.
 * @param {React.Dispatch<any>} dispatch Dispatch that is retrieved from reducer
 * @param {changeCallback} changeCallback A function that gets ran on every keystroke
 * @param {{header: int; body: int}} maxLength The largest length before an error message will show for the header and body
 * @return
 */
export function handleChangeTip(
  e,
  tipData,
  dispatch,
  changeCallback,
  maxLength
) {
  changeCallback();
  let isHeader = false;
  if (e.target.id.includes("mephisto-worker-experience-tips__tip-header-input"))
    isHeader = true;

  const headerLength = isHeader ? e.target.value.length : tipData.header.length;
  const bodyLength = isHeader ? tipData.text.length : e.target.value.length;

  if (headerLength > maxLength.header) dispatch({ type: "header-too-long" });
  else if (bodyLength > maxLength.body) {
    dispatch({ type: "body-too-long" });
  } else if (headerLength <= maxLength.header && bodyLength <= maxLength.body)
    dispatch({ type: "return-to-default" });
}

/**
 * Runs the change callback when typing occurs in a feedback textarea.
 * If the feedback text area content is too long, then change state
 * @param {React.ChangeEvent<HTMLInputElement>} e A typical react event
 * @param {any} state State that is retrived from reducer. It should have a status property.
 * @param {React.Dispatch<any>} dispatch Dispatch that is retrieved from reducer
 * @param {changeCallback} changeCallback A function that gets ran on every keystroke
 * @param {int} maxLength The largest length before an error message will show
 * @return
 */
export function handleChangeFeedback(
  e,
  state,
  dispatch,
  changeCallback,
  maxLength
) {
  changeCallback(e);
  if (e.target.value.length > maxLength && state.status !== 4) {
    dispatch({ type: "too-long" });
  } else if (e.target.value.length <= maxLength) {
    dispatch({ type: "return-to-default" });
  }
}
