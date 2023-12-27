/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import DebugPanel from "./DebugPanel";

export default function LayersPanel(props) {
  return (
    <div style={{ display: "flex", height: "100%", flexDirection: "column" }}>
      <div style={{ flex: 1, overflowY: "auto" }}>
        <div className="bp3-tree">
          <ul className="bp3-tree-node-list bp3-tree-root">{props.layers()}</ul>
        </div>
      </div>
      {props.showDebugPane ? <DebugPanel /> : null}
    </div>
  );
}
