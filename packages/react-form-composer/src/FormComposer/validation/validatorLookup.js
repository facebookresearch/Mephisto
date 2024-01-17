/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import fieldIsRequired from "./validators/fieldIsRequired";
import maxLengthSatisfied from "./validators/maxLengthSatisfied";
import minLengthSatisfied from "./validators/minLengthSatisfied";
import regexpSatisfied from "./validators/regexpSatisfied";

// Available name of validator for users in JSON-config -> validator-function
export const validatorFunctionsByConfigName = {
  "maxLength": maxLengthSatisfied,
  "minLength": minLengthSatisfied,
  "required": fieldIsRequired,
  "regexp": regexpSatisfied,
};
