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
 * @param {string[]} questionsFeedbackText
 * @param {bool} containsQuestions
 * @return {{text: text; type: "feedback"; }} An object that can be used as a parameter of the
 *                                            handleSubmitMetadata() method in the mephisto-task package
 */
export function createFeedback(
  generalFeedbackText,
  questionsFeedbackText,
  questions,
  containsQuestions
) {
  if (containsQuestions) {
    const isAllQuestionFeedbackStrings = questionsFeedbackText.every(
      (currentQuestionFeedbackText) =>
        currentQuestionFeedbackText &&
        typeof currentQuestionFeedbackText === "string"
    );
    if (!isAllQuestionFeedbackStrings) {
      throw new Error(
        "A feedback response to one of the questions is not a string"
      );
    }
    const questionsAndAnswers = questions.map((currentQuestion, index) => ({
      question: currentQuestion,
      text: questionsFeedbackText[index],
    }));

    return {
      data: questionsAndAnswers,
      type: "feedback",
    };
  } else {
    if (!generalFeedbackText || !(typeof generalFeedbackText === "string"))
      throw new Error("Feedback text is not a string");

    return {
      data: [{ question: "General Feedback", text: generalFeedbackText }],
      type: "feedback",
    };
  }
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
 * @param {string} generalFeedbackText
 * @param {React.Dispatch<React.SetStateAction<string>>} setGeneralFeedbackText
 * @param {string[]} questionsFeedbackText
 * @param {React.Dispatch<React.SetStateAction<string[]>>} setQuestionsFeedbackText
 * @param {string[]} questions
 * @param {bool} containsQuestions
 * @return
 */
export function handleFeedbackSubmit(
  handleSubmit,
  handleMetadataSubmit,
  dispatch,
  generalFeedbackText,
  setGeneralFeedbackText,
  questionsFeedbackText,
  setQuestionsFeedbackText,
  questions,
  containsQuestions
) {
  if (handleSubmit) handleSubmit(generalFeedbackText);
  else {
    dispatch({ type: "loading" });
    handleMetadataSubmit(
      createFeedback(
        generalFeedbackText,
        questionsFeedbackText,
        questions,
        containsQuestions
      )
    )
      .then((data) => {
        if (data.status === "Submitted metadata") {
          setGeneralFeedbackText("");
          setQuestionsFeedbackText(questionsFeedbackText.map(() => ""));
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
 * @param {{header: Number; body: Number}} maxLength The largest length before an error message will show for the header and body
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
  if (e.target.id.includes("mephisto-worker-addons-tips__header-input"))
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
 * Dispatches the correct action to handle length error
 * This is ran when the general feedback text (no questions) changes
 * @param {React.ChangeEvent<HTMLTextAreaElement>} e
 * @param {Number} maxLength
 * @param {{status: Number; text: string; errorIndexes: Set<Number>;}} state
 * @param {React.Dispatch<any>} dispatch
 */
export function dispatchFeedbackActionNoQuestions(
  e,
  maxLength,
  state,
  dispatch
) {
  if (e.target.value.length > maxLength && state.status !== 4) {
    dispatch({ type: "too-long" });
  } else if (e.target.value.length <= maxLength) {
    dispatch({ type: "return-to-default" });
  }
}

/**
 * Dispatches the correct action to handle length errors for any of the questions
 * This is ran when there are questions present.
 * @param {React.ChangeEvent<HTMLTextAreaElement>} e
 * @param {Number} maxLength
 * @param {Number} currentIndex
 * @param {React.Dispatch<any>} dispatch
 * @param {string[]} questionsFeedbackText
 */
export function dispatchFeedbackActionWithQuestions(
  e,
  maxLength,
  currentIndex,
  dispatch,
  questionsFeedbackText
) {
  const errorIndexes = new Set([]);
  for (let i = 0; i < questionsFeedbackText.length; i++) {
    if (currentIndex === i) {
      if (e.target.value.length > maxLength) {
        console.log("current", e.target.value.length);
        errorIndexes.add(i);
      } else if (errorIndexes.has(i)) {
        errorIndexes.remove(i);
      }
    } else {
      if (questionsFeedbackText[i].length > maxLength) {
        console.log("others", questionsFeedbackText[i].length);
        errorIndexes.add(i);
      } else if (errorIndexes.has(i)) {
        errorIndexes.remove(i);
      }
    }
  }
  if (errorIndexes.size > 0) {
    dispatch({ type: "multiple-errors", errorIndexes: errorIndexes });
  } else {
    dispatch({ type: "return-to-default" });
  }
}

/**
 * Determines if the submit button should be disabled.
 * There are different disabling conditions if there are questions present vs if there are no questions present.
 * @param {boolean} containsQuestions
 * @param {string} feedbackText
 * @param {string[]} questionsFeedbackText
 * @param {{status: Number; text: string; errorIndexes: Set<Number>;}} state
 * @returns {boolean}
 */
export function isSubmitButtonDisabled(
  containsQuestions,
  generalFeedbackText,
  questionsFeedbackText,
  state
) {
  if (containsQuestions) {
    return state.errorIndexes !== null || questionsFeedbackText.includes("");
  } else {
    return (
      generalFeedbackText.length <= 0 ||
      state.status === 1 ||
      state.status === 4
    );
  }
}

/**
 * Runs the change callback when typing occurs in a feedback textarea.
 * If the feedback text area content is too long, then change state
 * @param {React.ChangeEvent<HTMLInputElement>} e A typical react event
 * @param {any} state State that is retrived from reducer. It should have a status property.
 * @param {React.Dispatch<any>} dispatch Dispatch that is retrieved from reducer
 * @param {changeCallback} changeCallback A function that gets ran on every keystroke
 * @param {Number} maxLength The largest length before an error message will show
 * @return
 */
export function handleChangeFeedback(
  e,
  dispatchFeedbackAction,
  changeCallback
) {
  changeCallback(e);
  dispatchFeedbackAction();
}
/**
 * Collects all tips that should be displayed in the tips popup
 * @param {{header: string; text: string;}[]} list The array that is retrieved from the list prop
 * @param {any} taskConfig The object that you get from useMephistoTask()
 * @returns An array that includes both the default tips and the tips retrieved from the backend
 */
export function getTipsArr(list, taskConfig) {
  let tipsArr = [];
  if (list) tipsArr.concat(list);
  if (taskConfig && taskConfig["tips"])
    tipsArr = tipsArr.concat(taskConfig["tips"]);

  return tipsArr;
}
