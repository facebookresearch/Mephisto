// NOTE: that `react-form-composer` library must be set in webpack config as an alias.
import { validateFieldValue } from "react-form-composer";

export function onChangeCountry(
  formData, // React state for the entire form
  updateFormData, // callback to set the React state
  element, // "field", "section", or "submit button" element that invoked this trigger
  fieldValue, // (optional) current field value, if the `element` is a form field
  formFields, // Object containing all form fields as defined in 'form_config.json'
  ...args // Arguments for this trigger (taken from form config)
) {
  // By default, `id_section_second` section is collapsed, and `id_region` field is hidden.
  // Selecting "USA" in `id_country` should open that section, and display that field.
  const secondSectionElement = document.getElementById("id_section_second");
  const regionFieldElement = document.getElementById("id_region");

  if (fieldValue === "USA") {
    // Open `id_section_second` section
    secondSectionElement.classList.add("hidden");

    // If you want to check (during development) that you're assigning a valid value to a field,
    // use `validateFieldValue` function from form composer utils (see the import above).
    const newMottoValueIsValid = validateFieldValue(formFields.motto, "", true);
    if (!newMottoValueIsValid) {
      console.log(
        "Write additional log message or logic here " +
          "if logs with argument `writeConsoleLog` is not enough for you"
      );
    }

    updateFormData("motto", ""); // Clear field value in React state

    // Show `id_region` field
    regionFieldElement.closest(".field").classList.remove("hidden");
  } else {
    // Collapse `id_section_second` section
    secondSectionElement.classList.remove("hidden");

    // Hide `id_region` field
    regionFieldElement.closest(".field").classList.add("hidden");
    updateFormData("region", ""); // Clear field value in React state
  }
}

export function onClickSectionHeader(
  formData, // React state for the entire form
  updateFormData, // callback to set the React state
  element, // "field", "section", or "submit button" element that invoked this trigger
  fieldValue, // (optional) current field value, if the `element` is a form field
  formFields, // Object containing all form fields as defined in 'form_config.json'
  sectionName // Argument for this trigger (taken from form config)
) {
  // Do something when header is clicked (toggle a section content)
  alert(`${sectionName} section title clicked.`);
}
