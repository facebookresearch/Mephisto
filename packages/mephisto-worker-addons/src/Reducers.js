/**
 *
 * @param {*} state
 * @param {*} action
 * 0 -> nothing going on
 * 1 -> loading
 * 2 -> success
 * 3 -> error
 * @returns
 */

export function tipsReducer(state, action) {
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
      newState.text = "❌ Something went wrong during submitting";
      return newState;
    default:
      throw new Error();
  }
}
