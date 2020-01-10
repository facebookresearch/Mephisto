import React from "react";
import { Card, Colors, Icon, FormGroup, InputGroup } from "@blueprintjs/core";
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
    url: `architects/${selected || "none"}/arguments`
  });

  return (
    <div>
      {data.map((arch: any) => (
        <Card
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
              {data.args.map((field: any) => (
                <FormGroup
                  label={field.name}
                  labelInfo={field.helpText}
                  labelFor={"arch-" + field.name}
                >
                  <InputGroup
                    id={"arch-" + field.name}
                    placeholder={field.defaultValue}
                    defaultValue={field.defaultValue}
                  ></InputGroup>
                </FormGroup>
              ))}
            </div>
          )}
        />
      )}
    </div>
  );
}
