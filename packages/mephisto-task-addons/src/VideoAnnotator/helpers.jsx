/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { cloneDeep } from "lodash";

export function secontsToTime(seconds) {
  if (typeof seconds !== "number") {
    return "00:00";
  }

  let startIndex = 11;
  let endIndex = 19;
  if (seconds < 3600) {
    startIndex = 14;
  }

  return new Date(seconds * 1000).toISOString().substring(startIndex, endIndex);
}

export function convertInitialDataListsToObjects(data) {
  const _data = {};

  data.map((track, ti) => {
    const _track = cloneDeep(track);
    _track.segments = {};
    const initSegments = track.segments || [];

    initSegments.map((segment, si) => {
      _track.segments[si] = segment;
    });

    _data[ti] = _track;
  });

  return _data;
}

export function convertAnnotationTasksDataObjectsRoLists(data) {
  const _data = [];

  Object.values(data).map((track) => {
    const _track = cloneDeep(track);
    _track.segments = Object.values(track.segments || {});

    _data.push(_track);
  });

  return _data;
}
