/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import {
  TOKEN_END_REGEX,
  TOKEN_END_SYMBOLS,
  TOKEN_START_REGEX,
  TOKEN_START_SYMBOLS,
} from "./FormComposer/constants";
import { FormComposer } from "./FormComposer/FormComposer";
import {
  prepareFormData,
  prepareRemoteProcedures,
  procedureTokenRegex,
} from "./FormComposer/utils";

export {
  FormComposer,
  TOKEN_END_REGEX,
  TOKEN_END_SYMBOLS,
  TOKEN_START_REGEX,
  TOKEN_START_SYMBOLS,
  prepareFormData,
  prepareRemoteProcedures,
  procedureTokenRegex,
};
