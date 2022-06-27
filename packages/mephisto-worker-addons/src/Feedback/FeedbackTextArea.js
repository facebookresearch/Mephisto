import { handleChangeFeedback } from "../Functions";
function FeedbackTextArea({
  setTriggerRef,
  width,
  feedbackText,
  setFeedbackText,
  stylePrefix,
  state,
  dispatch,
  maxFeedbackLength,
}) {
  return (
    <textarea
      ref={setTriggerRef}
      style={{
        minWidth: width ? width : "18rem",
        width: width ? width : "18rem",
      }}
      onChange={(e) =>
        handleChangeFeedback(
          e,
          state,
          dispatch,
          (event) => setFeedbackText(event.target.value),
          maxFeedbackLength
        )
      }
      value={feedbackText}
      placeholder="Enter feedback text here"
      id={`${stylePrefix}text-area`}
    />
  );
}
export default FeedbackTextArea;
