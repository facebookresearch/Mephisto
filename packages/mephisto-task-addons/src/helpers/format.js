/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

export function pluralizeString(str, num, str_plural) {
  if (num !== 1) {
    if (!!str_plural) {
      return str_plural;
    }
    else{
      let pluralizedEnding = '';
      if (str.endsWith('s') || str.endsWith('ch')) {
        pluralizedEnding = 'es';
      }
      else if (str.endsWith('z')) {
        pluralizedEnding = 'zes';
      }
      else {
        pluralizedEnding = 's';
      }
      return `${str}${pluralizedEnding}`;
    }
  }

  return str;
}
