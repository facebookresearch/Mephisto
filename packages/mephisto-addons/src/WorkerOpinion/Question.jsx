/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React, { forwardRef } from "react";
import TextArea from "./TextArea.jsx";

const Question = forwardRef(
  (
    {
      className,
      containsQuestions,
      dispatch,
      index,
      maxTextAreaLength,
      placeholder,
      question,
      questionsTexts,
      setQuestionsTexts,
      state,
      stylePrefix,
      textAreaRows,
      textAreaWidth,
    },
    ref
  ) => (
    <div
      className={`${className ?? ""} ${stylePrefix}questions-container`}
      key={`question-${index}`}
    >
      <label className={`${stylePrefix}question`} htmlFor={`question-${index}`}>
        {question}
      </label>{" "}
      <TextArea
        containsQuestions={containsQuestions}
        dispatch={dispatch}
        id={`question-${index}`}
        index={index}
        maxLength={maxTextAreaLength}
        placeholder={placeholder}
        questionsTexts={questionsTexts}
        ref={ref}
        rows={textAreaRows}
        setText={(textValue) => {
          const tempQuestions = [...questionsTexts];
          tempQuestions[index] = textValue;
          setQuestionsTexts(tempQuestions);
        }}
        state={state}
        stylePrefix={stylePrefix}
        text={questionsTexts[index]}
        width={textAreaWidth}
      />
      {state.status === 5 && state.errorIndexes.has(index) && (
        <div
          className="mephisto-addons-worker-opinion__red-box"
          style={{ width: textAreaWidth }}
        >
          {state.text}
        </div>
      )}
    </div>
  )
);

export default Question;
