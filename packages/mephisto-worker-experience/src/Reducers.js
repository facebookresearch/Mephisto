/**
 * Manaages the state of the submission of a tip
 * @param {*} state
 * @param {*} action
 * 0 -> nothing going on
 * 1 -> loading
 * 2 -> success
 * 3 -> error
 * @returns
 */

export function tipReducer(state, action) {
  const newState = { ...state };
  switch (action.type) {
    case "return-to-default":
      newState.status = 0;
      newState.text = "";
      return newState;

    case "loading":
      newState.status = 1;
      newState.text = "Loading";
      return newState;
    case "success":
      newState.status = 2;
      newState.text = "✅ Your tip has been submitted for review";
      return newState;
    case "error":
      newState.status = 3;
      newState.text = "❌ Something went wrong when submitting your tip";
      return newState;
    default:
      throw new Error();
  }
}

/**
 * Manaages the state of the submission of feedback
 * @param {*} state
 * @param {*} action
 * 0 -> nothing going on
 * 1 -> loading
 * 2 -> success
 * 3 -> error
 * @returns
 */

export function feedbackReducer(state, action) {
  const newState = { ...state };
  switch (action.type) {
    case "return-to-default":
      newState.status = 0;
      newState.text = "";
      return newState;
    case "loading":
      newState.status = 1;
      newState.text = "Loading";
      return newState;
    case "success":
      newState.status = 2;
      newState.text = "✅ Your feedback has been submitted for review";
      return newState;
    case "error":
      newState.status = 3;
      newState.text = "❌ Something went wrong when submitting your feedback";
      return newState;
    case "too-long":
      newState.status = 4;
      newState.text = "📝 Your feedback message is too long";
      return newState;
    default:
      throw new Error();
  }
}
