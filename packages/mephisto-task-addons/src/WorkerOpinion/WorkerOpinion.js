/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import css from "!raw-loader!./WorkerOpinion.css";
import bootstrapCss from "!raw-loader!bootstrap/dist/css/bootstrap.css";
import React, { useEffect, useReducer, useState } from "react";
import { usePopperTooltip } from "react-popper-tooltip";
import Question from "./Question";
import { workerOpinionReducer } from "./Reducers";
import SubmitButton from "./SubmitButton";
import TextArea from "./TextArea";

const DEFAULT_MAX_TEXT_LENGTH = 700;
const DEFAULT_TEXTAREA_ROWS = 3;
const DEFAULT_TEXTAREA_WIDTH = "100%";
const defaultStateValue = {
  status: 0,
  text: "",
  errorIndexes: null,
};

function WorkerOpinion({
  questions,
  handleSubmit,
  maxTextLength,
  textAreaWidth,
}) {
  // To make classNames more readable
  const stylePrefix = `mephisto-task-addons-worker-opinion__`;

  // Setting defaults
  const maxTextAreaLength = maxTextLength
    ? maxTextLength
    : DEFAULT_MAX_TEXT_LENGTH;
  const modifiedTextAreaWidth = textAreaWidth
    ? textAreaWidth
    : DEFAULT_TEXTAREA_WIDTH;

  // For when there are questions
  const [questionsTexts, setQuestionsTexts] = useState([]);

  // For use when there are no questions
  const [generalText, setGeneralText] = useState("");

  // For showing attachments names
  const [attachmentsNames, setAttachmentsNames] = useState([]);
  const [attachmentsValue, setAttachmentsValue] = useState("");

  const [state, dispatch] = useReducer(workerOpinionReducer, defaultStateValue);

  const containsQuestions = questions?.length > 0;

  // Configuring react-popper-tooltip
  const { getTooltipProps, setTooltipRef, setTriggerRef } = usePopperTooltip(
    {
      trigger: null,
      visible: state.status === 2 || state.status === 3,
      offset: [0, 18],
      onVisibleChange: () => {},
    },
    {
      placement: "top-start",
    }
  );

  // Setting up the questionsTexts state based off of how many questions were set
  useEffect(() => {
    if (questions) {
      setQuestionsTexts(questions.map(() => ""));
    }
  }, [questions]);

  return (
    <>
      <div className={`alert alert-secondary`} role={"alert"}>
        <header className={`${stylePrefix}header-items`}>
          <h2 className={`${stylePrefix}header`}>
            Write opinion
            <small className={`${stylePrefix}subtitle`}>(optional)</small>
          </h2>
        </header>

        <hr />

        <section
          className={
            containsQuestions
              ? `${stylePrefix}items-vertical`
              : `${stylePrefix}items-horizontal`
          }
        >
          {containsQuestions ? (
            questions.map((question, index) => {
              return (
                <div className={"form-row mb-3"} key={`question-${index}`}>
                  <Question
                    className={"col"}
                    containsQuestions={containsQuestions}
                    dispatch={dispatch}
                    index={index}
                    maxTextAreaLength={maxTextAreaLength}
                    placeholder={"Answer the above question here"}
                    question={question}
                    questionsTexts={questionsTexts}
                    ref={setTriggerRef}
                    setQuestionsTexts={setQuestionsTexts}
                    state={state}
                    stylePrefix={stylePrefix}
                    textAreaRows={DEFAULT_TEXTAREA_ROWS}
                    textAreaWidth={modifiedTextAreaWidth}
                  />
                </div>
              );
            })
          ) : (
            <div className={"form-row mb-3"}>
              <TextArea
                className={"col"}
                containsQuestions={containsQuestions}
                dispatch={dispatch}
                id={`${stylePrefix}solo-textarea`}
                maxLength={maxTextAreaLength}
                ref={setTriggerRef}
                rows={DEFAULT_TEXTAREA_ROWS}
                setText={setGeneralText}
                state={state}
                stylePrefix={stylePrefix}
                text={generalText}
                width={modifiedTextAreaWidth}
              />
            </div>
          )}

          <div className={`${stylePrefix}attachments mb-3`}>
            <div className={"form-row mb-1"}>
              <span className={"col"}>
                {!attachmentsNames.length
                  ? "No files attached"
                  : attachmentsNames.map((a, i) => {
                      return (
                        <small key={`attach-${i}`}>
                          <b>
                            {a}
                            <br />
                          </b>
                        </small>
                      );
                    })}
              </span>
            </div>

            <div className={"form-row custom-file"}>
              <input
                accept={"image/jpeg,image/png,image/gif"}
                className={"custom-file-input col"}
                id={"id_attachments"}
                multiple={true}
                name={"attachments"}
                value={attachmentsValue}
                onChange={(e) => {
                  const fileNames = Object.values(e.target.files).map(
                    (file) => file.name
                  );
                  setAttachmentsNames(fileNames);
                  setAttachmentsValue(e.target.value);
                }}
                required={false}
                type={"file"}
              />

              <label className={"custom-file-label"} htmlFor={"id_attachments"}>
                Attach screenshots
                <small>(optional)</small>
              </label>
            </div>
          </div>

          {((!containsQuestions && state.status === 2) ||
            state.status === 3 ||
            state.status === 4) && (
            <div
              {...getTooltipProps({ className: "tooltip-container" })}
              ref={setTooltipRef}
              className={`${stylePrefix}${
                state.status === 2 ? "green" : "red"
              }-box`}
            >
              {state.text}
            </div>
          )}

          <div className={"form-row mb-3"}>
            <SubmitButton
              containsQuestions={containsQuestions}
              dispatch={dispatch}
              generalText={generalText}
              handleSubmit={handleSubmit}
              questions={questions}
              questionsTexts={questionsTexts}
              // TODO: Refactor this passing a bunch of `set` states.
              //  It should be one callback from here
              setAttachmentsNames={setAttachmentsNames}
              setAttachmentsValue={setAttachmentsValue}
              setGeneralText={setGeneralText}
              setQuestionsTexts={setQuestionsTexts}
              state={state}
              stylePrefix={stylePrefix}
            />

            {containsQuestions && state.status === 2 && (
              <div
                className={`${stylePrefix}green-box`}
                style={{ width: modifiedTextAreaWidth }}
              >
                {state.text}
              </div>
            )}
          </div>
        </section>
      </div>

      <style type={"text/css"}>
        {bootstrapCss}

        {css}
      </style>
    </>
  );
}

export default WorkerOpinion;
