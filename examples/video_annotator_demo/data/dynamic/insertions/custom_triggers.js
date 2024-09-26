/**
 * WARNING: Do not remove this file.
 * It is required for an import that can't be try-catched during the build or run time.
 * You should place your custom triggers here below this comment
 */

export function onFocusDescription(
  annotatorData, // React state for the entire annotator
  updateAnnotatorData, // callback to set the React state
  element, // "field", "section", or "submit button" element that invoked this trigger
  fieldValue, // (optional) current field value, if the `element` is a segment field
  segmentFields, // Object containing all segment fields as defined in 'unit_config.json'
  argumentFromConfig // Argument for this trigger (taken from annotator config)
) {
  console.log(`${argumentFromConfig} description was focused!`);
}
