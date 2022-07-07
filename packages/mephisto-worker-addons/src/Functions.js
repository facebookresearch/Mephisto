/**
 * @callback submitCallback
 */

/**
 * Creates a tip in the format that is accepted
 * by the handleMetadataSubmit function from the
 * mephisto-task library
 * @param {string} header The tip header
 * @param {string} text The tip text or a.k.a the tip body
 * @return {{header: string; text: string; type: string; }} An object that can be used as a parameter of the handleSubmitMetadata() method in the mephisto-task package
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
 * @return {{text: text; type: "feedback"; }} An object that can be used as a parameter of the handleSubmitMetadata() method in the mephisto-task package
 */
export function createFeedback(text) {
  if (!text || !(typeof text === "string"))
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
        if (data.status === "Submitted metadata") {
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

/**
 *
 * @param {{header: string; text: string;}[]} list The array that is retrieved from the list prop
 * @param {any} taskConfig The object that you get from useMephistoTask()
 * @returns An array that includes both the default tips and the tips retrieved from the backend
 */
export function getTipsArr(list, taskConfig) {
  let tipsArr = [];
  if (list) tipsArr.concat(list);
  if (taskConfig && taskConfig["metadata"] && taskConfig["metadata"]["tips"])
    tipsArr = tipsArr.concat(taskConfig["metadata"]["tips"]);

  return tipsArr;
}
