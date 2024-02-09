/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

let tokenProcedureResultMapping = {};

export function formatStringWithProcedureTokens(string) {
  if (string.includes("{{") && string.includes("}}")) {
    let _string = string;

    const procedureTokenRegex = /\{\{\s*([\w\(\)\"\'\/\.\_\-\:\{\}\\]+)\s*\}\}/gi;

    // Find list of  pairs [[token with brackets, procedure with arguments], ...]
    const matches = [...string.matchAll(procedureTokenRegex)];

    // Request all procedures and associate them with map key (token for this procedure)
    matches.forEach((match) => {
      const token = match[0];

      if (!tokenProcedureResultMapping.hasOwnProperty(token)) {
        const procedureCleanString = match[1].trim();
        const procedureName = procedureCleanString.split("(")[0];

        // If there's no global procedure (in `window`) with the name from the token,
        // we just skip the evaluation, and return the raw token string.
        // Normally all procedures must be defined as global vars before the form begins to render
        if (!window.hasOwnProperty(procedureName)) {
          console.error(`Could not find remote procedire ${procedureName}`);
          return string;
        }

        // Lookup the procedure in global variables and call it (note: all procedures are Promises)
        const procedurePromise = eval("window." + procedureCleanString);

        procedurePromise.then((response) => {
          tokenProcedureResultMapping[token] = response;
        }).catch((error) => {
          console.error(`Could not get remote response for ${procedureName}`, error);
        });
      }
    });

    // Override tokens with values received from the server
    Object.keys(tokenProcedureResultMapping).forEach((token) => {
      _string = _string.replaceAll(token, tokenProcedureResultMapping[token]);
    });

    return _string;
  }

  return string;
}
