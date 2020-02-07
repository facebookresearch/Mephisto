import React from "react";
import {
  Card,
  Colors,
  Icon,
  FormGroup,
  InputGroup,
  Checkbox
} from "@blueprintjs/core";
import useAxios from "axios-hooks";
import { createAsync } from "../../lib/Async";

type ArchitectParams = any;
const BlueprintParamsAsync = createAsync<ArchitectParams>();

export default function ArchitectSelect({
  data,
  onUpdate
}: {
  data: any;
  onUpdate: Function;
}) {
  const [selected, setSelected] = React.useState(null);
  const paramsInfo = useAxios({
    url: `architect/${selected || "none"}/options`
  });

  return (
    <div>
      {data.map((arch: any) => (
        <Card
          key={arch}
          interactive={arch !== selected}
          style={{
            marginBottom: 10,
            backgroundColor: arch === selected ? undefined : undefined
          }}
          onClick={() => setSelected(arch)}
        >
          <Icon
            icon={arch === selected ? "tick-circle" : "circle"}
            color={arch === selected ? Colors.GREEN4 : Colors.GRAY4}
            title={"Selected"}
            style={{ marginRight: 10 }}
          />
          {arch}
        </Card>
      ))}
      {selected && (
        <BlueprintParamsAsync
          info={paramsInfo}
          onLoading={() => <span>Loading...</span>}
          onError={() => <span>Error</span>}
          onData={({ data }) => (
            <div style={{ margin: "20px 0" }}>
              {Object.values(data.options)
                .flatMap((opt: any) => Object.values(opt.args))
                .map((field: any) => {
                  return field.type === "bool" ? (
                    <div key={field.dest}>
                      <Checkbox
                        defaultChecked={field.default}
                        label={field.dest}
                      />
                      <p className="bp3-text-muted">{field.help}</p>
                    </div>
                  ) : (
                    <FormGroup
                      key={field.dest}
                      label={field.dest}
                      labelInfo={field.help}
                      labelFor={"arch-" + field.dest}
                    >
                      <InputGroup
                        id={"arch-" + field.dest}
                        placeholder={field.default}
                        defaultValue={field.default}
                      ></InputGroup>
                    </FormGroup>
                  );
                })}
            </div>
          )}
        />
      )}
    </div>
  );
}
