const FORBIDDEN_WORDS = ["fool", "silly", "stupid"];

export function checkForbiddenWords(field, value, check) {
  if (!check) {
    return null;
  }

  let invalid = false;

  FORBIDDEN_WORDS.forEach((word) => {
    if (value.includes(word)) {
      invalid = true;
    }
  });

  if (invalid) {
    return `Field cannot contain any of these words: ${FORBIDDEN_WORDS.join(
      ", "
    )}.`;
  }

  return null;
}
