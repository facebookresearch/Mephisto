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
