/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from "react";
import { FormGroup, InputGroup, Checkbox } from "@blueprintjs/core";

function FormField({
  prefix,
  onUpdate,
  field,
}: {
  prefix: string;
  onUpdate: any;
  field: any;
}) {
  const id = prefix + "|" + field.dest + "|" + field.option_string;
  const dispatch = (value: any) => {
    onUpdate({
      [id]: value,
    });
  };

  React.useEffect(() => {
    if (field.type === "str2bool") {
      dispatch(!!field.default); // for bools, type cast the default value
    } else if (!!field.default) {
      dispatch(field.default); // for non-bools, just use the uncasted value
    }
  }, [field.default]);

  return field.type === "str2bool" ? (
    <div key={field.dest}>
      <Checkbox
        defaultChecked={!!field.default}
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
