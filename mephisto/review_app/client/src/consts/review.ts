/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

export const ReviewType = {
  APPROVE: "approve",
  REJECT: "reject",
  SOFT_REJECT: "softReject",
};

export const MESSAGES_IFRAME_DATA_KEY = "IFRAME_DATA";

export const MESSAGES_IN_REVIEW_FILE_DATA_KEY = "IN_REVIEW_FILE_DATA";

export const FileType = {
  AUDIO: "audio",
  IMAGE: "image",
  PDF: "pdf",
  VIDEO: "video",
};

export const FILE_TYPE_BY_EXT = {
  png: FileType.IMAGE,
  jpg: FileType.IMAGE,
  jpeg: FileType.IMAGE,
  gif: FileType.IMAGE,
  heic: FileType.IMAGE,
  heif: FileType.IMAGE,
  webp: FileType.IMAGE,
  bmp: FileType.IMAGE,
  mkv: FileType.VIDEO,
  mp4: FileType.VIDEO,
  webm: FileType.VIDEO,
  mp3: FileType.AUDIO,
  ogg: FileType.AUDIO,
  wav: FileType.AUDIO,
  pdf: FileType.PDF,
};

export const AUDIO_TYPES_BY_EXT = {
  mp3: "audio/mpeg",
  ogg: "audio/ogg",
  wav: "audio/wav",
};

export const VIDEO_TYPES_BY_EXT = {
  mkv: "video/x-matroska",
  mp4: "video/mp4",
  webm: "video/webm",
  mov: "video/quicktime",
  avi: "video/x-msvideo",
};
