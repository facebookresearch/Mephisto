/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/**
 * Manaages the state of the submission of Worker Opinion
 * @param {*} state
 * @param {*} action
 * 0 -> nothing going on
 * 1 -> loading
 * 2 -> success
 * 3 -> error
 * @returns
 */

export function workerOpinionReducer(state, action) {
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
      newState.text = "✅ Your opinion has been submitted for review";
      newState.errorIndexes = null;
      return newState;
    case "error":
      newState.status = 3;
      newState.text = "❌ Something went wrong when submitting your opinion";
      newState.errorIndexes = null;
      return newState;

    case "too-long":
      newState.status = 4;
      newState.text = "📝 Your opinion message is too long";
      newState.errorIndexes = null;
      return newState;

    // This case can only happen when there are questions present
    // There needs to be error checking for the multiple opinion
    case "multiple-errors":
      newState.status = 5;
      newState.errorIndexes = action.errorIndexes;
      newState.text = "📝 Your opinion message for this question is too long";
      return newState;

    default:
      throw new Error();
  }
}
