/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import CollapsableBlock from "components/CollapsableBlock/CollapsableBlock";
import * as React from "react";
import JSONPretty from 'react-json-pretty';
import "./InitialParameters.css";


type InitialParametersPropsType = {
  data: object;
  open?: boolean;
  isJSON: boolean;
};

function InitialParameters(props: InitialParametersPropsType) {
  const { data, open, isJSON } = props;

  return (
    <CollapsableBlock
      className={"initial-parameters"}
      open={open}
      title={"Initial Parameters"}
      tooltip={"Toggle initial Unit parameters data"}
    >
      {isJSON ? (
        <JSONPretty
          className={"json-pretty"}
          data={data}
          space={4}
        />
      ) : (
        <div>{JSON.stringify(data)}</div>
      )}
    </CollapsableBlock>
  );
}

export default InitialParameters;
