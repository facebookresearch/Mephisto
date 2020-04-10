const queryString = require("query-string");

export function getMturkTaskInfo() {
  const {
    assignmentId,
    hitId,
    turkSubmitTo,
    workerId,
    REVIEW_WITH_DATA,
    ...otherParams
  } = queryString.parse(window.location.search);

  const isReview = REVIEW_WITH_DATA !== undefined;
  const isPreview =
    (!assignmentId || assignmentId === "ASSIGNMENT_ID_NOT_AVAILABLE") &&
    !isReview;

  const fullSubmitUrl = turkSubmitTo
    ? turkSubmitTo + "/mturk/externalSubmit"
    : undefined;

  return {
    params: otherParams,
    mturk: {
      assignmentId,
      hitId,
      turkSubmitTo: fullSubmitUrl,
      workerId
    },
    reviewData: REVIEW_WITH_DATA,
    isPreview,
    isReview,
    isLive: !(isPreview || isReview)
  };
}
export function serialize(data, encodeURI) {
  const jsonData = JSON.stringify(data);
  return encodeURI ? encodeURIComponent(jsonData) : jsonData;
}
export function deserialize(data, decodeURI) {
  try {
    const stringData = decodeURI ? decodeURIComponent(data) : data;
    return JSON.parse(stringData);
  } catch {
    return undefined;
  }
}
export const serializeURI = data => serialize(data, true);
export const deserializeURI = data => deserialize(data, true);

