import React from "react";
import { Layers } from "../Task";
import DebugPanel from "./DebugPanel";

export default function ContextPanel() {
  return (
    <div style={{ display: "flex", height: "100%", flexDirection: "column" }}>
      <div style={{ flex: 1 }}>
        <div className="bp3-tree">
          <ul className="bp3-tree-node-list bp3-tree-root">
            <Layers />
          </ul>
        </div>
      </div>
      <DebugPanel />
    </div>
  );
}
