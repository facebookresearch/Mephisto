/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

export const DELAY_PROGRESSBAR_RESIZING_MSEC = 1000;

export const STORAGE_PRESAVED_ANNOTATION_TRACKS_KEY = "annotation_tracks";

// In case if user does not specify any field
export const DEFAULT_SEGMENT_FIELDS = [
  {
    id: "id_title",
    label: "Segment name",
    name: "title",
    type: "input",
  },
];

export const INIT_ANNOTATION_TRACK = {
  title: "",
  segments: {},
};

// When we click on segment, we simulate clicking on track as well, and it must be first,
// but setting states is async
export const DELAY_CLICK_ON_SECTION_MSEC = 200;

export const START_NEXT_SECTION_PLUS_SEC = 0;

export const COLORS = [
  "blue",
  "green",
  "orange",
  "purple",
  "red",
  "yellow",
  "brown",
];

export const INIT_SECTION = {
  description: "",
  end_sec: 0,
  start_sec: 0,
  title: "",
};

export const MIN_SEGMENT_WIDTH_PX = 6;

export const POPOVER_INVALID_SEGMENT_CLASS = "with-segment-validation";

export const POPOVER_INVALID_SEGMENT_PROPS = {
  "data-html": true,
  "data-placement": "top",
  "data-content": "Please fix provided data before continuing",
  "data-toggle": "popover",
  "data-trigger": "hover",
};

export const CHAPTERS_SETTINGS = {
  kind: "chapters",
  label: "Segments",
  language: "en",
  mode: "showing",
};
