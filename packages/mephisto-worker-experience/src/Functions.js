/**
 * Creates a tip in the format that is accepted
 * by the handleMetadataSubmit function from the
 * mephisto-task library
 * @param {string} header The tip header
 * @param {string} text The tip text or a.k.a the tip body
 * @return {{header: string; text: string; type: string; }} An object that can be used as a parameter of the handleSubmitMetadata() method in the mephisto-task package
 */
export function createTip(header, text) {
  if (!header || !(typeof header === "string") || !(header instanceof String))
    throw new Error("Tip header is not a string");

  if (!text || !(typeof text === "string") || !(text instanceof String))
    throw new Error("Tip text is not a string");

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
 * @param {string} text The feedback text
 * @return {{text: text; type: "feedback"; }} An object that can be used as a parameter of the handleSubmitMetadata() method in the mephisto-task package
 */
export function createFeedback(text) {
  if (!text || !(typeof text === "string") || !(text instanceof String))
    throw new Error("Feedback text is not a string");

  return {
    text: text,
    type: "feedback",
  };
}
