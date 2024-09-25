#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from datetime import timedelta
from typing import List
from typing import TypedDict
from typing import Union

from webvtt import Caption
from webvtt import WebVTT


DEFAULT_SEGMENT_KEYS = [
    "end_sec",
    "start_sec",
    "title",
]

DEFAULT_TRACK_KEYS = ["segments", "title"]

WEBVTT_CAPTION_NAME_FORMAT = "{segment_title} ({track_title})"


class VideoAnnotatorSegmentType(TypedDict):
    description: str
    end_sec: float
    start_sec: float
    title: str


class VideoAnnotatorTrackType(TypedDict):
    segments: List[VideoAnnotatorSegmentType]
    title: str


class VideoAnnotatorDataType(TypedDict):
    tracks: List[VideoAnnotatorTrackType]


def _make_vtt_timestamp_from_seconds(seconds: float) -> str:
    _timedelta = timedelta(seconds=seconds)

    days = _timedelta.days
    hours, remainder = divmod(_timedelta.seconds, 3600)

    hours = days * 24 + hours
    minutes, seconds = divmod(remainder, 60)
    mseconds = _timedelta.microseconds

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{mseconds:03d}"


def _validate_annotation_tracks(
    unit_config_data: dict,
    annotation_data: VideoAnnotatorDataType,
) -> bool:
    config_segment_fields = unit_config_data.get("annotator", {}).get("segment_fields", [])
    config_segment_keys = [f["name"] for f in config_segment_fields]
    segment_keys_set = set(DEFAULT_SEGMENT_KEYS + config_segment_keys)

    if not isinstance(annotation_data, dict):
        return False

    annotation_tracks = annotation_data.get("tracks")

    if not isinstance(annotation_tracks, list):
        return False

    for track in annotation_tracks:
        if not isinstance(track, dict):
            return False

        track_has_all_keys = set(DEFAULT_TRACK_KEYS).issubset(set(track.keys()))

        if not track_has_all_keys:
            return False

        for segment in track["segments"]:
            if not isinstance(segment, dict):
                return False

            segment_has_all_keys = set(segment.keys()).issubset(segment_keys_set)

            if not segment_has_all_keys:
                return False

    return True


class SegmentToCaptionTextConverter:
    STRING_FIELDS_TYPES = [
        "email",
        "input",
        "number",
        "password",
        "textarea",
    ]

    OPTIONS_FIELDS_TYPES = [
        "radio",
        "select",
    ]

    def __init__(self, unit_config_data: dict, segment: dict):
        self.segment = segment

        config_segment_fields = unit_config_data.get("annotator", {}).get("segment_fields", [])
        self.segment_fields_for_text = [
            f for f in config_segment_fields if f["name"] not in DEFAULT_SEGMENT_KEYS
        ]

    @staticmethod
    def _convert_string_field(field: dict, value: str) -> str:
        field_label = field.get("label")

        if not field_label:
            return value

        return f"{field_label}: {value}"

    @staticmethod
    def _convert_options_field(field: dict, value: Union[str, List[str]]) -> str:
        options_dict = {o["value"]: o["label"] for o in field.get("options", [])}
        is_multiple = field.get("multiple")
        if is_multiple:
            value = ", ".join([options_dict[i] for i in value])
        else:
            value = options_dict[value]

        field_label = field.get("label")

        if not field_label:
            return value

        return f"{field_label}: {value}"

    @staticmethod
    def _convert_checkbox_field(field: dict, value: dict) -> str:
        options_dict = {o["value"]: o["label"] for o in field.get("options", [])}
        value = ", ".join([options_dict[l] for l, v in value.items() if v is True])

        field_label = field.get("label")

        if not field_label:
            return value

        return f"{field_label}: {value}"

    def get_text(self) -> str:
        text_lines = []

        for field in self.segment_fields_for_text:
            field_name = field["name"]
            field_type = field["type"]
            field_value = self.segment.get(field_name)

            if not field_value:
                continue

            field_text = ""
            if field_type in self.STRING_FIELDS_TYPES:
                field_text = self._convert_string_field(field, field_value)
            elif field_type in self.OPTIONS_FIELDS_TYPES:
                field_text = self._convert_options_field(field, field_value)
            elif field_type == "checkbox":
                field_text = self._convert_checkbox_field(field, field_value)
            else:
                pass

            if not field_text:
                continue

            text_lines.append(field_text)

        return "\n".join(text_lines)


def convert_annotation_tracks_to_webvtt(
    task_name: str,
    unit_config_data: dict,
    annotation_data: VideoAnnotatorDataType,
) -> Union[str, None]:
    # If no tracks, return None instead of string with WebVTT header
    if not annotation_data:
        return None

    # Validate data
    is_valid = _validate_annotation_tracks(unit_config_data, annotation_data)
    if not is_valid:
        return None

    webvtt = WebVTT(
        header_comments=[f"Mephisto Task \"{task_name}\""],
        footer_comments=["Copyright (c) Meta Platforms and its affiliates."],
    )

    # Update segments' titles with track title and sort by start
    segments = [
        {
            **segment,
            "title": WEBVTT_CAPTION_NAME_FORMAT.format(
                segment_title=segment["title"],
                track_title=track["title"],
            ),
        }
        for track in annotation_data["tracks"]
        for segment in track["segments"]
    ]
    sorted_segments_by_start = sorted(segments, key=lambda k: k["start_sec"])

    for segment in sorted_segments_by_start:
        vtt_caption = Caption(
            start=_make_vtt_timestamp_from_seconds(segment["start_sec"]),
            end=_make_vtt_timestamp_from_seconds(segment["end_sec"]),
            text=SegmentToCaptionTextConverter(unit_config_data, segment).get_text(),
            identifier=segment["title"],
        )
        webvtt.captions.append(vtt_caption)

    return webvtt.content
