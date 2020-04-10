import React from "react";
import {
  getMturkTaskInfo,
  serialize,
  deserialize,
  serializeURI,
  deserializeURI
} from "mturk-utils";

export { serialize, deserialize, serializeURI, deserializeURI };

export function useMturkTask() {
  return React.useMemo(getMturkTaskInfo, []);
}

export function SubmitTask({ task, data, onSubmit, encodeURI, render }) {
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const formRef = React.useRef(null);
  const submitForm = () => {
    formRef.current && formRef.current.submit();
    setIsSubmitting(false);
  };
  const handleSubmit = () => {
    setIsSubmitting(true);
    if (!onSubmit) {
      submitForm();
    }
    const result = onSubmit(data);
    if (!isPromise(result)) {
      submitForm();
    }
    result.then(() => submitForm());
  };

  return (
    <div>
      <form
        ref={formRef}
        action={task.mturk.turkSubmitTo}
        method="POST"
        style={{ margin: 0, padding: 0, width: 0, height: 0 }}
      >
        <input
          readOnly
          hidden={true}
          type="text"
          name="assignmentId"
          value={task.mturk.assignmentId}
        />
        <input
          readOnly
          hidden={true}
          type="text"
          name="data"
          value={serialize(data, encodeURI)}
        />
      </form>
      {render({ handleSubmit, isSubmitting })}
    </div>
  );
}

export function Task({
  renderPreview,
  renderReview,
  renderLive,
  defaultReviewState = {},
  initialLiveState = {}
}) {
  if (!(renderPreview && renderLive)) {
    throw new Error(
      "The two states for renderPreview and renderLive must be defined."
    );
  }

  const task = useMturkTask();
  const [state, setState] = React.useState(initialLiveState);

  if (task.isPreview) {
    return renderPreview({ task });
  }
  if (task.isReview) {
    const reviewData =
      task.isReview && task.reviewData
        ? deserializeURI(task.reviewData)
        : defaultReviewState;
    return renderReview({ reviewData, task });
  }

  if (task.isLive) {
    return renderLive({ task, state, setState });
  }
}

function isPromise(obj) {
  return (
    !!obj &&
    (typeof obj === "object" || typeof obj === "function") &&
    typeof obj.then === "function"
  );
}
