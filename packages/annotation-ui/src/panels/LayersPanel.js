import React, { useContext } from "react";
import { Context } from "../model/Store";
import { Layers } from "../Task";
import DebugPanel from "./DebugPanel";

export default function ContextPanel() {
  return (
    <div style={{ display: "flex", height: "100%", flexDirection: "column" }}>
      <div style={{ flex: 1 }}>
        <Layers />
      </div>
      <DebugPanel />
    </div>
  );
}
