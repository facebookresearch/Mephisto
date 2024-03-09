export function onChangeCountry(
  formData, // React state for the entire form
  updateFormData, // callback to set the React state
  element, // "field", "section", or "submit button" element that invoked this trigger
  fieldValue, // (optional) current field value, if the `element` is a form field
  ...args // Arguments for this trigger (taken from form config)
) {
  // By default, `id_section_second` section is collapsed, and `id_region` field is hidden.
  // Selecting "USA" in `id_country` should open that section, and display that field.
  const secondSectionElement = document.getElementById("id_section_second");
  const mottoFieldElement = document.getElementById("id_motto");
  const regionFieldElement = document.getElementById("id_region");

  if (fieldValue === "USA") {
    // Open `id_section_second` section
    secondSectionElement.classList.add("hidden");
    mottoFieldElement.value = "";

    // Show `id_region` field
    regionFieldElement.closest(".field").classList.remove("hidden");
  } else {
    // Collapse `id_section_second` section
    secondSectionElement.classList.remove("hidden");

    // Hide `id_region` field
    regionFieldElement.closest(".field").classList.add("hidden");
    regionFieldElement.value = ""; // Clean value in HTML-element
    updateFormData("region", ""); // Clean value in react state
  }
}

export function onClickSectionHeader(
  formData, // React state for the entire form
  updateFormData, // callback to set the React state
  element, // "field", "section", or "submit button" element that invoked this trigger
  fieldValue, // (optional) current field value, if the `element` is a form field
  sectionName // Argument for this trigger (taken from form config)
) {
  // Do something when header is clicked (toggle a section content)
  alert(`${sectionName} section title clicked.`);
}
