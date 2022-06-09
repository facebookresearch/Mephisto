/**
 * Creates a tip in the format that is accepted
 * by the handleMetadataSubmit function from the
 * mephisto-task library
 * @param {string} header
 * @param {string} text
 */
export function createTip(header, text) {
  if (!header || !typeof header === "string" || !header instanceof String) {
    return new Promise(function (resolve, reject) {
      reject("Tip header is not a string");
    });
  }
  if (!text || !typeof text === "string" || !text instanceof String) {
    return new Promise(function (resolve, reject) {
      reject("Tip text is not a string");
    });
  }
  return {
    header: header,
    text: text,
    type: "tips",
  };
}

/**
 * Creates a feedback item in the format that is accepted
 * by the handleMetadataSubmit function from the
 * mephisto-task library
 * @param {string} text
 */
export function createFeedback(text) {
  if (!text || !typeof text === "string" || !text instanceof String) {
    return new Promise(function (resolve, reject) {
      reject("Feedback text is not a string");
    });
  }
  return {
    text: text,
    type: "feedback",
  };
}
