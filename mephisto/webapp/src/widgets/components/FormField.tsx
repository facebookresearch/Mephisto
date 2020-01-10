import React from "react";
import { FormGroup, InputGroup } from "@blueprintjs/core";

function FormField({
  prefix,
  onUpdate,
  field
}: {
  prefix: string;
  onUpdate: any;
  field: any;
}) {
  const id = prefix + "-" + field.name;
  const dispatch = (value: any) => {
    onUpdate({
      [id]: value
    });
  };

  React.useEffect(() => {
    if (!!field.defaultValue) {
      dispatch(field.defaultValue);
    }
  }, [field.defaultValue]);

  return (
    <FormGroup label={field.name} labelInfo={field.helpText} labelFor={id}>
      <InputGroup
        id={id}
        placeholder={field.defaultValue}
        defaultValue={field.defaultValue}
        onChange={(e: any) => dispatch(e.target.value)}
      ></InputGroup>
    </FormGroup>
  );
}

export default FormField;
