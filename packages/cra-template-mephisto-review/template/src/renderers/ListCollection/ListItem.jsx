/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import { H6 } from "@blueprintjs/core";

function ListItem({ item }) {
  return (
    <>
      <pre>{JSON.stringify(item && item.data)}</pre>
      <H6>
        <b>ID: {item && item.id}</b>
      </H6>
    </>
  );
}

export default ListItem;
