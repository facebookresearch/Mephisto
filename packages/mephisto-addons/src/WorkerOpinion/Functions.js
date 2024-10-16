/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/**
 * @callback submitCallback
 * @callback changeCallback
 */

const ADDON_TYPE = "worker_opinion";
const HIDE_ALERT_DELAY = 5000;

/**
 * Creates a Worker Opinion item in the format that is accepted
 * by the handleMetadataSubmit function from the
 * `mephisto-core` library.
 *
 * @param {string} generalText The general Worker Opinion text
 * @param {string[]} questionsTexts
 * @param {string[]} questions
 * @param {bool} containsQuestions
 * @return {{data: [{question: string, text: string}], type: string}} An object that can be used
 *  as a parameter of the handleSubmitMetadata() method in the `mephisto-core` package
 */
export function createWorkerOpinion(
  generalText,
  questionsTexts,
  questions,
  containsQuestions
) {
  let opinionData = {};
  const formData = new FormData();

  if (containsQuestions) {
    const isAllQuestionStrings = questionsTexts.every(
      (currentQuestionText) =>
        currentQuestionText && typeof currentQuestionText === "string"
    );

    if (!isAllQuestionStrings) {
      throw new Error(
        "A Worker Opinion response to one of the questions is not a string"
      );
    }

    opinionData.questions = questions.map((currentQuestion, index) => ({
      question: currentQuestion,
      text: questionsTexts[index],
    }));
  } else {
    if (!generalText || !(typeof generalText === "string"))
      throw new Error("Worker Opinion text is not a string");

    opinionData.questions = [
      { question: "General Worker Opinion", text: generalText },
    ];
  }

  const data = {
    [ADDON_TYPE]: opinionData,
  };

  // Append files in Form Data next to JSON data
  const filesInfo = [];
  const fileInputs = document.querySelectorAll("input[type='file'].metadata");
  fileInputs.forEach((input) => {
    if (input.files?.length) {
      Object.values(input.files).forEach((file) => {
        formData.append(input.name, file, file.name);
        filesInfo.push({
          lastModified: file.lastModified ? file.lastModified : -1,
          name: file.name ? file.name : "",
          size: file.size ? file.size : -1,
          type: file.type ? file.type : "",
          filename: file.filename,
          fieldname: file.fieldname,
        });
      });
    }
  });

  formData.set("data", JSON.stringify(data)); // Main JSON data to save in storage
  formData.set("files", JSON.stringify(filesInfo)); // Info for saving files in storage
  formData.set("type", ADDON_TYPE); // Type of metadata

  return formData;
}

/** When handleSubmit is not defined, this
 * function submits the current Worker Opinion data to the backend.
 * It also does success/error handling.
 *
 * When handleSubmit is defined, the handleSubmit
 * function is ran with the workerOpinionData obj as its first parameter.
 *
 * @param {submitCallback} handleSubmit
 * @param {submitCallback} handleMetadataSubmit
 * @param {React.Dispatch<any>} dispatch
 * @param {string} generalText
 * @param {React.Dispatch<React.SetStateAction<string>>} setGeneralText
 * @param {string[]} questionsTexts
 * @param {React.Dispatch<React.SetStateAction<string[]>>} setQuestionsTexts
 * @param {string[]} questions
 * @param {bool} containsQuestions
 * @return
 */
export function handleWorkerOpinionSubmit(
  handleSubmit,
  handleMetadataSubmit,
  dispatch,
  generalText,
  setGeneralText,
  questionsTexts,
  setQuestionsTexts,
  questions,
  containsQuestions,
  setAttachmentsNames,
  setAttachmentsValue
) {
  if (handleSubmit) {
    handleSubmit(generalText);
  } else {
    dispatch({ type: "loading" });

    handleMetadataSubmit(
      createWorkerOpinion(
        generalText,
        questionsTexts,
        questions,
        containsQuestions
      )
    )
      .then((data) => {
        if (data.status === "Submitted metadata") {
          setGeneralText("");
          setQuestionsTexts(questionsTexts.map(() => ""));
          setAttachmentsNames([]);
          setAttachmentsValue("");

          dispatch({ type: "success" });

          setTimeout(() => {
            dispatch({ type: "return-to-default" });
          }, HIDE_ALERT_DELAY);
        }
      })
      .catch((error) => {
        console.error("createWorkerOpinion", error);
        dispatch({ type: "error" });

        setTimeout(() => {
          dispatch({ type: "return-to-default" });
        }, HIDE_ALERT_DELAY);
      });
  }
}

/**
 * Dispatches the correct action to handle length error
 * This is run when the general Worker Opinion text (no questions) changes.
 *
 * @param {React.ChangeEvent<HTMLTextAreaElement>} e
 * @param {Number} maxLength
 * @param {{status: Number; text: string; errorIndexes: Set<Number>;}} state
 * @param {React.Dispatch<any>} dispatch
 */
export function dispatchWorkerOpinionActionNoQuestions(
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
 * This is run when there are questions present.
 *
 * @param {React.ChangeEvent<HTMLTextAreaElement>} e
 * @param {Number} maxLength
 * @param {Number} currentIndex
 * @param {React.Dispatch<any>} dispatch
 * @param {string[]} questionsTexts
 */
export function dispatchWorkerOpinionActionWithQuestions(
  e,
  maxLength,
  currentIndex,
  dispatch,
  questionsTexts
) {
  const errorIndexes = new Set([]);

  for (let i = 0; i < questionsTexts.length; i++) {
    if (currentIndex === i) {
      if (e.target.value.length > maxLength) {
        errorIndexes.add(i);
      } else if (errorIndexes.has(i)) {
        errorIndexes.remove(i);
      }
    } else {
      if (questionsTexts[i].length > maxLength) {
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
 * There are different disabling conditions if there are questions present vs
 * if there are no questions present.
 *
 * @param {boolean} containsQuestions
 * @param {string} generalText
 * @param {string[]} questionsTexts
 * @param {{status: Number; text: string; errorIndexes: Set<Number>;}} state
 * @returns {boolean}
 */
export function isSubmitButtonDisabled(
  containsQuestions,
  generalText,
  questionsTexts,
  state
) {
  if (containsQuestions) {
    return state.errorIndexes !== null || questionsTexts.includes("");
  } else {
    return generalText.length <= 0 || state.status === 1 || state.status === 4;
  }
}

/**
 * Runs the change callback when typing occurs in a Worker Opinion textarea.
 * If the Worker Opinion textarea content is too long, then change state.
 *
 * @param {React.ChangeEvent<HTMLInputElement>} e A typical react event
 * @param {React.Dispatch<any>} dispatchAction Dispatch that is retrieved from reducer
 * @param {changeCallback} changeCallback A function that gets ran on every keystroke
 * @return
 */
export function handleChangeWorkerOpinion(e, dispatchAction, changeCallback) {
  changeCallback(e);
  dispatchAction();
}
