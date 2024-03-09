/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { cloneDeep } from "lodash";
import {
  TOKEN_END_REGEX,
  TOKEN_END_SYMBOLS,
  TOKEN_START_REGEX,
  TOKEN_START_SYMBOLS,
} from "./constants";

// TODO: Remove this after finding out what is the problem
//  with not sending `agent_id` under `subject_id` field in websocket message
const WAIT_FOR_AGENT_ID_MSEC = 1000;

let tokenProcedureResultMapping = {};

const procedureRegex = /(.*?)/;
const optionalSpacesRegex = /\s*/;
const openingRegex = new RegExp(
  TOKEN_START_REGEX.source + optionalSpacesRegex.source,
  "gi"
);
const closingRegex = new RegExp(
  optionalSpacesRegex.source + TOKEN_END_REGEX.source,
  "gi"
);
export const procedureTokenRegex = new RegExp(
  openingRegex.source + procedureRegex.source + closingRegex.source,
  "gi"
);

const ProcedureName = {
  GET_MULTIPLE_PRESIGNED_URLS: "getMultiplePresignedUrls",
  GET_PRESIGNED_URL: "getPresignedUrl",
};

let urlTotokenProcedureMapping = {};

export function formatStringWithProcedureTokens(string, errorCallback) {
  if (!string || typeof string !== "string") {
    return string;
  }

  if (
    string.includes(TOKEN_START_SYMBOLS) &&
    string.includes(TOKEN_END_SYMBOLS)
  ) {
    let _string = string;

    // Find array of pairs [[<token with brackets>, <procedure code with arguments>], ...]
    const matches = [...string.matchAll(procedureTokenRegex)];

    // Request all procedures and associate them with map key (token for this procedure)
    matches.forEach((match) => {
      const entireToken = match[0];

      // If we already have this token in map, we do not request it again
      if (!tokenProcedureResultMapping.hasOwnProperty(entireToken)) {
        const procedureCleanString = match[1].trim();
        const procedureName = procedureCleanString.split("(")[0];

        // If there's no global procedure (in `window`) with the name from the token,
        // we just skip the evaluation, and return the raw token string.
        // Normally all procedures must be defined as global vars before the form begins to render
        if (!window.hasOwnProperty(procedureName)) {
          console.error(`Could not find remote procedure ${procedureName}`);
          return string;
        }

        // Lookup the procedure in global variables and call it (note: all procedures are Promises)
        const procedurePromise = eval("window." + procedureCleanString);

        procedurePromise
          .then((response) => {
            tokenProcedureResultMapping[entireToken] = response;
          })
          .catch((error) => {
            if (errorCallback) {
              errorCallback(error);
            }
            console.error(
              `Could not get remote response for '${procedureName}'`,
              error
            );
          });
      }
    });

    // Override tokens with values received from the server
    Object.keys(tokenProcedureResultMapping).forEach((token) => {
      _string = _string.replaceAll(token, tokenProcedureResultMapping[token]);
    });

    return _string;
  }

  return string;
}

function _getUrlsFromString(string) {
  let urls = [];

  if (
    string.includes(TOKEN_START_SYMBOLS) &&
    string.includes(TOKEN_END_SYMBOLS)
  ) {
    // Find array of pairs [[<token with brackets>, <procedure code with arguments>], ...]
    const matches = [...string.matchAll(procedureTokenRegex)];
    matches.forEach(([token, procedureCode]) => {
      if (procedureCode.includes(ProcedureName.GET_MULTIPLE_PRESIGNED_URLS)) {
        const procedureCodeWithUrlMatches = [
          ...procedureCode.matchAll(/\(\"(.+?)\"\)/gi),
        ];
        if (
          procedureCodeWithUrlMatches.length &&
          procedureCodeWithUrlMatches[0].length === 2
        ) {
          const procedureCodeUrl = procedureCodeWithUrlMatches[0][1];
          urls.push(procedureCodeUrl);
          urlTotokenProcedureMapping[procedureCodeUrl] = token;
        }
      }
    });
  }

  return [...new Set(urls)];
}

export function _getAllUrlsToPresign(formConfig) {
  let urls = new Set();

  function _extractUrlsToPresignFromConfigItem(configItem) {
    Object.values(configItem).forEach((value) => {
      if (typeof value === "string") {
        const valueUrls = _getUrlsFromString(value);
        if (valueUrls.length) {
          urls = new Set([...urls, ...valueUrls]);
        }
      }
    });
  }

  // Any form object (form, section, field, etc.) whose attributes can contain tokens
  const configItemsToFindUrls = [];
  configItemsToFindUrls.push(formConfig);
  formConfig.sections.map((section) => {
    configItemsToFindUrls.push(section);
    section.fieldsets.map((fieldset) => {
      configItemsToFindUrls.push(fieldset);
      fieldset.rows.map((row) => {
        configItemsToFindUrls.push(row);
        row.fields.map((field) => {
          configItemsToFindUrls.push(field);
        });
      });
    });
  });

  configItemsToFindUrls.forEach((formItem) => {
    _extractUrlsToPresignFromConfigItem(formItem);
  });

  return [...urls];
}

export function _replaceUrlsWithPresignedUrlsInFormData(
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
        const token = urlTotokenProcedureMapping[originalUrl];
        if (token) {
          configItem[key] = value.replaceAll(token, presignedUrl);
        }
      }
    });
  }

  let _taskData = cloneDeep(taskData);
  presignedUrls.forEach(([originalUrl, presignedUrl]) => {
    // Any form object (form, section, field, etc.) whose attributes can contain tokens
    const configItemsToFindUrls = [];

    configItemsToFindUrls.push(_taskData.form);

    _taskData.form.sections.forEach((section) => {
      configItemsToFindUrls.push(section);
      section.fieldsets.map((fieldset) => {
        configItemsToFindUrls.push(fieldset);
        fieldset.rows.map((row) => {
          configItemsToFindUrls.push(row);
          row.fields.map((field) => {
            configItemsToFindUrls.push(field);
          });
        });
      });
    });

    configItemsToFindUrls.forEach((formItem) => {
      _replaceTokensWithUrlsConfigItem(formItem, originalUrl, presignedUrl);
    });

    return _taskData;
  });

  return _taskData;
}

function _prepareFormDataWithUrlsToPresign(
  taskConfigData,
  setFormDataState,
  setLoadingFormDataState,
  setFormComposerRenderingErrorsState
) {
  // Get URLs to presign from the whole config
  const urlsToPresign = _getAllUrlsToPresign(taskConfigData.form);

  // If there's nothing to do, just set initial config as is
  if (!urlsToPresign.length) {
    setFormDataState(taskConfigData.form);
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
  setLoadingFormDataState(true);

  // Make a request to the server. Note: timeout is a hack (see the comment next to the constant)
  setTimeout(() => {
    window
      .getMultiplePresignedUrls(urlsToPresign)
      .then((response) => {
        setLoadingFormDataState(false);
        const updatedTaskData = _replaceUrlsWithPresignedUrlsInFormData(
          taskConfigData,
          response
        );
        setFormDataState(updatedTaskData.form);
      })
      .catch((error) => {
        setLoadingFormDataState(false);
        setFormComposerRenderingErrorsState(error);
      });
  }, WAIT_FOR_AGENT_ID_MSEC);
}

export function prepareFormData(
  taskConfigData,
  setFormDataState,
  setLoadingFormDataState,
  setFormComposerRenderingErrorsState
) {
  // 1. Presign URLs
  _prepareFormDataWithUrlsToPresign(
    taskConfigData,
    setFormDataState,
    setLoadingFormDataState,
    setFormComposerRenderingErrorsState
  );

  // 2. TODO: Add additional steps here
}

function _prepareRemoteProceduresForPresignUrls(remoteProcedureCollection) {
  window[ProcedureName.GET_PRESIGNED_URL] = remoteProcedureCollection(
    ProcedureName.GET_PRESIGNED_URL
  );
  window[ProcedureName.GET_MULTIPLE_PRESIGNED_URLS] = remoteProcedureCollection(
    ProcedureName.GET_MULTIPLE_PRESIGNED_URLS
  );
}

export function prepareRemoteProcedures(remoteProcedureCollection) {
  // 1. Presign URLs
  _prepareRemoteProceduresForPresignUrls(remoteProcedureCollection);

  // 2. TODO: Add additional steps here
}

export function setPageTitle(title) {
  const titleElement = document.querySelector("title");
  titleElement.innerText = title;
}
