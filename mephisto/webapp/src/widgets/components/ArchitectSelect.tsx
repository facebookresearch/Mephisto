/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from "react";
import {
  Card,
  Colors,
  Icon,
  FormGroup,
  InputGroup,
  Checkbox,
} from "@blueprintjs/core";
import useAxios from "axios-hooks";
import { createAsync } from "../../lib/Async";
import OptionsForm from "./OptionsForm";

type ArchitectParams = any;
const ArchitectParamsAsync = createAsync<ArchitectParams>();

export default function ArchitectSelect({
  data,
  onUpdate,
}: {
  data: any;
  onUpdate: Function;
}) {
  const [selected, setSelected] = React.useState(null);
  const paramsInfo = useAxios({
    url: `architect/${selected || "none"}/options`,
  });

  return (
    <div>
      {data.map((arch: any) => (
        <Card
          key={arch}
          interactive={arch !== selected}
          style={{
            marginBottom: 10,
            backgroundColor: arch === selected ? undefined : undefined,
          }}
          onClick={() => {
            setSelected(arch);
            onUpdate({ architect: arch });
          }}
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
        <ArchitectParamsAsync
          info={paramsInfo}
          onLoading={() => <span>Loading...</span>}
          onError={() => <span>Error</span>}
          onData={({ data }) => (
            <OptionsForm
              onUpdate={onUpdate}
              options={data.options}
              prefix="arch"
            />
          )}
        />
      )}
    </div>
  );
}
