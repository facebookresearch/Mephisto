/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/**
 * Collection of methods to act as tools tests can use
 */

/**
 * Delays program for specified time in milliseconds. Must be used in async mode.
 * @param {Number} time time in milliseconds to delay process.
 */
export const delay = (time) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(2);
    }, time);
  });
};
