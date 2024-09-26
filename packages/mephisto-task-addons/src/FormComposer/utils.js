/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { cloneDeep } from "lodash";
import {
  FieldType,
  TOKEN_END_REGEX,
  TOKEN_END_SYMBOLS,
  TOKEN_START_REGEX,
  TOKEN_START_SYMBOLS,
} from "./constants";

// This list can be expanded if needed
const ACCEPTED_SCALAR_TRIGGER_ARGUMENT_TYPES = [
  "string",
  "boolean",
  "number",
  "object",
];

// TODO: Remove this after finding out what is the problem
//  with not sending `agent_id` under `subject_id` field in websocket message
export const WAIT_FOR_AGENT_ID_MSEC = 1000;

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

export const ProcedureName = {
  GET_MULTIPLE_PRESIGNED_URLS: "getMultiplePresignedUrls",
  GET_PRESIGNED_URL: "getPresignedUrl",
};

let urlToTokenProcedureMapping = {};

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

export function getFormatStringWithTokensFunction(inReviewState) {
  const func = inReviewState
    ? (v, _) => {
        return v;
      } // Return value as is, ignoring whole formatting
    : formatStringWithProcedureTokens;

  return func;
}

export function getUrlsFromString(string, mapping) {
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
          mapping[procedureCodeUrl] = token;
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
        const valueUrls = getUrlsFromString(value, urlToTokenProcedureMapping);
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
        const token = urlToTokenProcedureMapping[originalUrl];
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

export function isObjectEmpty(_object) {
  return Object.keys(_object).length === 0;
}

export function runCustomTrigger(
  // Args used in this util
  elementTriggersConfig, // 'triggers' value defined in 'unit_config.json' file
  elementTriggerName,
  customTriggers,
  // Args passed directly into the trigger function
  formData, // React state for the entire form
  updateFormData, // callback to set the React state
  element, // "field", "section", or "submit button" element that invoked this trigger
  fieldValue, // (optional) Current field value, if the `element` is a form field
  formFields // (optional) Object containing all form fields as defined in 'unit_config.json'
) {
  // Exit if the element that doesn't have any triggers defined (no logs required)
  if (!elementTriggersConfig || isObjectEmpty(elementTriggersConfig)) {
    return;
  }

  const elementTriggerConfig = elementTriggersConfig[elementTriggerName];

  // Exit if the element doesn't have this specific triggers defined (no logs required)
  if (!elementTriggerConfig) {
    return;
  }

  // Exit if the element has this trigger set, but custom triggers were not passed
  if (!customTriggers) {
    console.error(
      `Ignoring trigger "${elementTriggerName}" invokation - no custom triggers passed.`
    );
    return;
  }

  // Extract name of custom trigger function from the trigger config.
  // Exit if trigger config doesn't contain custom function name
  let triggerFnName;

  const triggerConfigIsArray = Array.isArray(elementTriggerConfig);
  const triggerConfigIsScalar =
    !triggerConfigIsArray && // because `typeof <array> === "object"`
    ACCEPTED_SCALAR_TRIGGER_ARGUMENT_TYPES.includes(
      typeof elementTriggerConfig
    );

  if (triggerConfigIsArray && [1, 2].includes(elementTriggerConfig.length)) {
    triggerFnName = elementTriggerConfig[0];
  } else if (triggerConfigIsScalar) {
    triggerFnName = elementTriggerConfig;
  } else {
    console.error(
      `Invalid format of trigger "${elementTriggerName}" config: ${elementTriggerConfig}. ` +
        `It must be either a string (function name), ` +
        `or a list (first element is function name, second element is its args).`
    );
    return;
  }

  // Get Custom trigger function
  const triggerFn = customTriggers[triggerFnName];

  // Exit if the custom function was not defined
  if (!triggerFn) {
    console.error(
      `Function not found for trigger "${elementTriggerName}". ` +
        `Please ensure a functionwith that name is defined in 'custom_triggers.js' file ` +
        `and 'unit_config.json' indicates correct custom function name for this trigger config.`
    );
    return;
  }

  // Extract arguments of custom trigger function from the trigger config.
  let triggerFnArgs;
  if (triggerConfigIsScalar) {
    // If trigger config doesn't contain arguments, we just won't pass any trigger arguments
    triggerFnArgs = [];
  } else if (
    triggerConfigIsArray &&
    [1, 2].includes(elementTriggerConfig.length)
  ) {
    triggerFnArgs = elementTriggerConfig[1];
    // if trigger function arg is a scalar, turn it into a 1-item array, for consistency
    triggerFnArgs = Array.isArray(triggerFnArgs)
      ? triggerFnArgs
      : [triggerFnArgs];
  } else {
    console.error(
      `Trigger "${elementTriggerName}" config for "${elementTriggerName}" ` +
        `is longer than 2 items: ${elementTriggerConfig}`
    );
    return;
  }

  // Run custom trigger
  try {
    triggerFn(
      formData,
      updateFormData,
      element,
      fieldValue,
      formFields,
      ...triggerFnArgs
    );
  } catch (error) {
    const textAboutElement = fieldValue
      ? `Field "${element.name}" value: ${fieldValue}. `
      : `Element config name: ${elementTriggerName}. `;
    console.error(
      `Running custom trigger error. ` +
        textAboutElement +
        `Element trigger name: ${elementTriggerName}. ` +
        `Element trigger config: ${elementTriggerConfig}. ` +
        `Trigger function name: ${triggerFnName}. ` +
        `Trigger function args: ${triggerFnArgs}. ` +
        `Error: ${error}.`
    );
  }
}

export function getDefaultFormFieldValue(field, initialFormData) {
  if (initialFormData) {
    return initialFormData[field.name];
  }

  if (field.value !== undefined) {
    return field.value;
  }

  if (
    [
      FieldType.EMAIL,
      FieldType.HIDDEN,
      FieldType.INPUT,
      FieldType.NUMBER,
      FieldType.PASSWORD,
      FieldType.RADIO,
      FieldType.TEXTAREA,
    ].includes(field.type)
  ) {
    return "";
  } else if (field.type === FieldType.CHECKBOX) {
    const allItemsNotCheckedValue = Object.fromEntries(
      field.options.map((o) => [o.value, !!o.checked])
    );
    return allItemsNotCheckedValue;
  } else if (field.type === FieldType.SELECT) {
    return field.multiple ? [] : "";
  }

  return null;
}

/**
 * A helper function to check during development, that your custom triggers
 * assign correct values to form fields (in case you want to change them programmatically).
 * @param {object} field FormComposer field
 * @param {any} value FormComposer field value
 * @param {boolean} writeConsoleLog If `true`, writes detailed error logs in browser console
 * @return {boolean} If `true`, the field value is valid
 */
export function validateFieldValue(field, value, writeConsoleLog) {
  // No need to validate absence of value
  if ([null, undefined].includes(value)) {
    return true;
  }

  if ([null, undefined].includes(field)) {
    console.error(`Argument 'field' cannot be '${field}'.`);
    return false;
  }

  let valueIsValid = true;
  let logMessage = "";

  if (
    [
      FieldType.EMAIL,
      FieldType.HIDDEN,
      FieldType.INPUT,
      FieldType.NUMBER,
      FieldType.PASSWORD,
      FieldType.RADIO,
      FieldType.TEXTAREA,
    ].includes(field.type)
  ) {
    if (typeof value !== "string") {
      valueIsValid = false;
      logMessage = `Value must be a 'string' for field '${field.name}' with type '${field.type}'.`;
    } else {
      if (field.type === FieldType.RADIO) {
        const availableOptions = Object.values(field.options).map(
          (o) => o.value
        );

        if (!availableOptions.includes(value)) {
          valueIsValid = false;
          logMessage =
            `Incorrect value for field '${field.name}' with type '${field.type}'. ` +
            `Available options: ${availableOptions}. `;
        }
      }
    }
  } else if (field.type === FieldType.CHECKBOX) {
    if (typeof value === "object" && !Array.isArray(value)) {
      const availableOptions = Object.values(field.options).map((o) => o.value);

      const allParamsAreBooleansWithCorrectOption = Object.entries(value).every(
        ([k, v]) => {
          return availableOptions.includes(k) && typeof v === "boolean";
        }
      );

      if (!allParamsAreBooleansWithCorrectOption) {
        valueIsValid = false;
        logMessage =
          `All value parameters must be 'boolean' ` +
          `for field '${field.name}' with type '${field.type}'. ` +
          `Available options: ${availableOptions}. `;
      }
    } else {
      valueIsValid = false;
      logMessage =
        `Value must be an 'object' with boolean parameters ` +
        `for field '${field.name}' with type '${field.type}'.`;
    }
  } else if (field.type === FieldType.SELECT) {
    if (field.multiple) {
      if (!Array.isArray(value)) {
        valueIsValid = false;
        logMessage =
          `Value must be an 'array' for field '${field.name}' with type '${field.type}' ` +
          `and '"multiple": true'.`;
      } else {
        const availableOptions = Object.values(field.options).map(
          (o) => o.value
        );

        const allParamsAreStringsWithCorrectOption = value.every((v) => {
          return typeof v === "string" && availableOptions.includes(v);
        });

        if (!allParamsAreStringsWithCorrectOption) {
          valueIsValid = false;
          logMessage =
            `All value parameters must be 'string' ` +
            `for field '${field.name}' with type '${field.type}' and '"multiple": true'. ` +
            `Available options: ${availableOptions}. `;
        }
      }
    } else {
      if (typeof value !== "string") {
        valueIsValid = false;
        logMessage =
          `Value must be a 'string' ` +
          `for field '${field.name}' with type '${field.type}' and '"multiple": false'.`;
      }
    }
  }

  if (writeConsoleLog && !valueIsValid && logMessage) {
    logMessage += ` You passed value '${JSON.stringify(
      value
    )}' with type '${typeof value}'`;
    console.error(logMessage);
  }

  if (writeConsoleLog && valueIsValid) {
    console.info(
      `Value '${JSON.stringify(value)}' for field '${field.name}' ` +
        `with type '${typeof value}' is valid`
    );
  }

  return valueIsValid;
}
