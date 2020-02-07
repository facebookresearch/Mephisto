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
    if (!!field.default) {
      dispatch(field.default);
    }
  }, [field.default]);

  return (
    <FormGroup label={field.dest} labelInfo={field.help} labelFor={id}>
      <InputGroup
        id={id}
        placeholder={field.default}
        defaultValue={field.default}
        onChange={(e: any) => dispatch(e.target.value)}
      ></InputGroup>
    </FormGroup>
  );
}

export default FormField;
