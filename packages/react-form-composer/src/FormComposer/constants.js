export const DEFAULT_COLLAPSABLE = true;

export const DEFAULT_INITIALLY_COLLAPSED = false;

export const TOKEN_START_SYMBOLS = "{{";

export const TOKEN_END_SYMBOLS = "}}";

export const TOKEN_START_REGEX = /\{\{/;

export const TOKEN_END_REGEX = /\}\}/;

export const MESSAGES_IN_REVIEW_FILE_DATA_KEY = "IN_REVIEW_FILE_DATA";

export const FieldType = {
  CHECKBOX: "checkbox",
  EMAIL: "email",
  FILE: "file",
  HIDDEN: "hidden",
  INPUT: "input",
  NUMBER: "number",
  PASSWORD: "password",
  RADIO: "radio",
  SELECT: "select",
  TEXTAREA: "textarea",
};

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
