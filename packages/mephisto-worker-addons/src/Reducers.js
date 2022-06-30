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
    case "header-too-long":
      newState.status = 4;
      newState.text = "📝 Your tip header is too long";
      return newState;
    case "body-too-long":
      newState.status = 5;
      newState.text = "📝 Your tip body is too long";
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
      newState.errorIndexes = null;
      return newState;
    case "loading":
      newState.status = 1;
      newState.text = "Loading";
      newState.errorIndexes = null;
      return newState;
    case "success":
      newState.status = 2;
      newState.text = "✅ Your feedback has been submitted for review";
      newState.errorIndexes = null;
      return newState;
    case "error":
      newState.status = 3;
      newState.text = "❌ Something went wrong when submitting your feedback";
      newState.errorIndexes = null;
      return newState;

    case "too-long":
      newState.status = 4;
      newState.text = "📝 Your feedback message is too long";
      newState.errorIndexes = null;
      return newState;

    // This case can only happen when there are questions present
    // There needs to be error checking for the multiple feedback
    case "multiple-errors":
      newState.status = 5;
      newState.errorIndexes = action.errorIndexes;
      newState.text = "📝 Your feedback message for this question is too long";
      return newState;

    default:
      throw new Error();
  }
}
