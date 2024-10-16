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
  avi: "video/x-msvideo",
  mkv: "video/x-matroska",
  mov: "video/quicktime",
  mp4: "video/mp4",
  mpeg: "video/mpeg",
  webm: "video/webm",
};

export const NEW_QUALIFICATION_NAME_LENGTH = 50;

export const NEW_QUALIFICATION_DESCRIPTION_LENGTH = 500;

export const EDIT_GRANTED_QUALIFICATION_VALUE_LENGTH = 50;

export const EDIT_GRANTED_QUALIFICATION_EXPLANATION_LENGTH = 500;

export const STATUS_COLOR_CLASS_MAPPING = {
  accepted: "text-success",
  approved: "text-success",
  rejected: "text-danger",
  soft_rejected: "text-warning",
};
