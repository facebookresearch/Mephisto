/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from "react";
import FormField from "./FormField";
import { Checkbox, Card } from "@blueprintjs/core";

function OptionsForm({
  prefix,
  onUpdate,
  options,
}: {
  prefix: string;
  onUpdate: any;
  options: any;
}) {
  React.useEffect(() => {
    onUpdate("CLEAR_" + prefix);
    Object.values(options)
      .flatMap((opt: any) => Object.values(opt.args))
      .forEach((field: any) => {
        const id = prefix + "|" + field.dest + "|" + field.option_string;
        onUpdate({
          [id]: field.default,
        });
      });
  }, [options]);

  return (
    <div>
      <div style={{ margin: "20px 0" }}>
        <Card className="bp3-elevation-2">
          {Object.values(options)
            .flatMap((opt: any) => Object.values(opt.args))
            .map((field: any) => {
              return (
                <FormField
                  key={prefix + field.dest}
                  prefix={prefix}
                  onUpdate={onUpdate}
                  field={field}
                />
              );
            })}
        </Card>
      </div>
    </div>
  );
}

export default OptionsForm;
