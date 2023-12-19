export const MAX_LENGTH_ERROR_MESSAGE_KEY = "max-length";
export const MIN_LENGTH_ERROR_MESSAGE_KEY = "min-length";
export const REGEXP_ERROR_MESSAGE_KEY = "regexp";
export const REQUIRED_ERROR_MESSAGE_KEY = "required";

export const validationErrorMessagesByName = {
  [MAX_LENGTH_ERROR_MESSAGE_KEY]: (n) => `Value should be no more than ${n} characters.`,
  [MIN_LENGTH_ERROR_MESSAGE_KEY]: (n) => `Value should be at least ${n} characters long.`,
  [REGEXP_ERROR_MESSAGE_KEY]: "Incorrectly formatted input.",
  [REQUIRED_ERROR_MESSAGE_KEY]: "This field is required.",
};
