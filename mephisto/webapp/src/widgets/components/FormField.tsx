import React from "react";
import { FormGroup, InputGroup, Checkbox } from "@blueprintjs/core";

function FormField({
  prefix,
  onUpdate,
  field
}: {
  prefix: string;
  onUpdate: any;
  field: any;
}) {
  const id = prefix + "-" + field.dest;
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

  return field.type === "bool" ? (
    <div key={field.dest}>
      <Checkbox
        defaultChecked={field.default}
        label={field.dest}
        onChange={(e: any) => {
          dispatch(e.target.checked);
        }}
      />
      <p className="bp3-text-muted">{field.help}</p>
    </div>
  ) : (
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
