/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import CollapsableBlock from "components/CollapsableBlock/CollapsableBlock";
import * as React from "react";
import "./WorkerOpinionCollapsable.css";

type WorkerOpinionCollapsablePropsType = {
  className?: string;
  data: WorkerOpinionType;
  onClickOnAttachment: (file: WorkerOpinionAttachmentType) => void;
  open?: boolean;
  title?: string | React.ReactElement;
};

function WorkerOpinionCollapsable(props: WorkerOpinionCollapsablePropsType) {
  const { className, data, onClickOnAttachment, open, title } = props;

  const _title = title || "Worker Opinion";

  return (
    <CollapsableBlock
      className={`worker-opinion ${className || ""}`}
      title={_title}
      open={open}
      tooltip={"Toggle Worker Opinion data"}
    >
      {/* Questions */}
      <div className={"questions"}>
        {data.questions.map(
          (question: WorkerOpinionQuestionType, index: number) => {
            return (
              <div
                className={"question"}
                key={`worker-opinion-question-${index}`}
              >
                <div className={"question-title"}>{question.question}</div>
                <pre className={"question-answer"}>{question.answer}</pre>
              </div>
            );
          }
        )}
      </div>

      {/* Attachments */}
      <div className={"attachments"}>
        <div className={"attachments-title"}>Attachments</div>

        {data.attachments.map(
          (attachement: WorkerOpinionAttachmentType, index: number) => {
            return (
              <div
                className={"attachment text-primary"}
                onClick={() => onClickOnAttachment(attachement)}
                key={`worker-opinion-attachment-${index}`}
              >
                {attachement.originalname}
              </div>
            );
          }
        )}
      </div>
    </CollapsableBlock>
  );
}

export default WorkerOpinionCollapsable;
