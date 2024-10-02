/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { cloneDeep } from "lodash";
import {
  getUrlsFromString,
  ProcedureName,
  WAIT_FOR_AGENT_ID_MSEC,
} from "../FormComposer/utils";
import { secontsToTime } from "./helpers.jsx";

let urlToTokenProcedureMapping = {};

export function _getAllUrlsToPresign(annotatorConfig) {
  let urls = new Set();

  function _extractUrlsToPresignFromConfigItem(configItem) {
    Object.values(configItem).forEach((value) => {
      if (typeof value === "string") {
        const valueUrls = getUrlsFromString(value, urlToTokenProcedureMapping);
        if (valueUrls.length) {
          urls = new Set([...urls, ...valueUrls]);
        }
      }
    });
  }

  // Any annotator object (title, instruction, segment_fields, etc.)
  // whose attributes can contain tokens
  const configItemsToFindUrls = [];
  configItemsToFindUrls.push(annotatorConfig);
  annotatorConfig.segment_fields.map((field) => {
    configItemsToFindUrls.push(field);
  });

  configItemsToFindUrls.forEach((configItem) => {
    _extractUrlsToPresignFromConfigItem(configItem);
  });

  return [...urls];
}

export function _replaceUrlsWithPresignedUrlsInAnnotatorData(
  taskData,
  presignedUrls
) {
  function _replaceTokensWithUrlsConfigItem(
    configItem,
    originalUrl,
    presignedUrl
  ) {
    Object.entries(configItem).forEach(([key, value]) => {
      if (typeof value === "string") {
        const token = urlToTokenProcedureMapping[originalUrl];
        if (token) {
          configItem[key] = value.replaceAll(token, presignedUrl);
        }
      }
    });
  }

  let _taskData = cloneDeep(taskData);
  presignedUrls.forEach(([originalUrl, presignedUrl]) => {
    // Any annotator object (title, instruction, segment_fields, etc.)
    // whose attributes can contain tokens
    const configItemsToFindUrls = [];

    configItemsToFindUrls.push(_taskData.annotator);

    _taskData.annotator.segment_fields.forEach((field) => {
      configItemsToFindUrls.push(field);
    });

    configItemsToFindUrls.forEach((configItem) => {
      _replaceTokensWithUrlsConfigItem(configItem, originalUrl, presignedUrl);
    });

    return _taskData;
  });

  return _taskData;
}

function _prepareAnnotatorDataWithUrlsToPresign(
  taskConfigData,
  setAnnotatorDataState,
  setLoadingAnnotatorDataState,
  setVideoAnnotatorRenderingErrorsState
) {
  // Get URLs to presign from the whole config
  const urlsToPresign = _getAllUrlsToPresign(taskConfigData.annotator);

  // If there's nothing to do, just set initial config as is
  if (!urlsToPresign.length) {
    setAnnotatorDataState(taskConfigData.annotator);
    return false;
  }

  // Procedure `getMultiplePresignedUrls` must be set up to perform this preparation
  if (!window.hasOwnProperty(ProcedureName.GET_MULTIPLE_PRESIGNED_URLS)) {
    console.error(
      `'${ProcedureName.GET_MULTIPLE_PRESIGNED_URLS}' function was not defined on the server side.`
    );
    return false;
  }

  // Enable preloader
  setLoadingAnnotatorDataState(true);

  // Make a request to the server. Note: timeout is a hack (see the comment next to the constant)
  setTimeout(() => {
    window
      .getMultiplePresignedUrls(urlsToPresign)
      .then((response) => {
        setLoadingAnnotatorDataState(false);
        const updatedTaskData = _replaceUrlsWithPresignedUrlsInAnnotatorData(
          taskConfigData,
          response
        );
        setAnnotatorDataState(updatedTaskData.annotator);
      })
      .catch((error) => {
        setLoadingAnnotatorDataState(false);
        setVideoAnnotatorRenderingErrorsState(error);
      });
  }, WAIT_FOR_AGENT_ID_MSEC);
}

export function prepareVideoAnnotatorData(
  taskConfigData,
  setAnnotatorDataState,
  setLoadingAnnotatorDataState,
  setVideoAnnotatorRenderingErrorsState
) {
  // 1. Presign URLs
  _prepareAnnotatorDataWithUrlsToPresign(
    taskConfigData,
    setAnnotatorDataState,
    setLoadingAnnotatorDataState,
    setVideoAnnotatorRenderingErrorsState
  );

  // 2. TODO: Add additional steps here
}

export function validateTimeFieldsOnSave(
  annotationTrack,
  segmentToChange,
  selectedSegment
) {
  const errors = [];
  const validation = {};

  // If start is greater than end
  if (segmentToChange.start_sec > segmentToChange.end_sec) {
    errors.push(`Start of the segment cannot be greater than end of it.`);
    validation.end_sec = false;
  }

  // If segment is inside another segment
  Object.entries(annotationTrack.segments).map(([segmentIndex, segment]) => {
    // Skip currently saving segment
    if (String(segmentIndex) === String(selectedSegment)) {
      return;
    }

    let hasOverlapping = false;

    if (
      segmentToChange.start_sec > segment.start_sec &&
      segmentToChange.start_sec < segment.end_sec
    ) {
      hasOverlapping = true;
      validation.start_sec = false;
    }

    if (
      segmentToChange.end_sec > segment.start_sec &&
      segmentToChange.end_sec < segment.end_sec
    ) {
      hasOverlapping = true;
      validation.end_sec = false;
    }

    if (hasOverlapping) {
      errors.push(
        `You cannot start or end a segment in already created segment before: ` +
          `${segment.title} ${secontsToTime(
            segment.start_sec
          )} - ${secontsToTime(segment.end_sec)}`
      );
    }
  });

  return {
    errors: errors,
    fields: validation,
  };
}
