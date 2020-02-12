import React from "react";
import FormField from "./FormField";
import { Checkbox } from "@blueprintjs/core";

function OptionsForm({
  prefix,
  onUpdate,
  options
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
          [id]: field.default
        });
      });
  }, [options]);

  return (
    <div>
      <div style={{ margin: "20px 0" }}>
        {Object.values(options)
          .flatMap((opt: any) => Object.values(opt.args))
          .map((field: any) => {
            return (
              <FormField prefix={prefix} onUpdate={onUpdate} field={field} />
            );
          })}
      </div>
    </div>
  );
}

export default OptionsForm;
