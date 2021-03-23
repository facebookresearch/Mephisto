import React from "react";
import { useStore } from "../model/Store";

import { Tabs, Tab } from "@blueprintjs/core";

function DebugPanel() {
  const { state } = useStore();
  const { debug, ...remainderState } = state;

  const displayState = remainderState.screenshot;

  return (
    <div style={{ height: 200 }} className="bp3-dark">
      <div style={{ height: "100%" }} className="bp3-menu bp3-elevation-1">
        <Tabs
          style={{ height: "100%" }}
          animate={true}
          id="TabsExample"
          key={"horizontal"}
          renderActiveTabPanelOnly={true}
        >
          <Tab
            id="state"
            title="Inspect State"
            panel={
              <code style={{ fontSize: 12 }}>
                {JSON.stringify(displayState, null, 2)}
              </code>
            }
          />
          <Tab
            id="actions"
            title="Actions fired"
            panel={
              <div style={{ overflowY: "auto" }}>
                {(state.debug?.actionsFired || []).map((a, idx) => (
                  <p key={idx}>{a.type}</p>
                ))}
              </div>
            }
          />
        </Tabs>
      </div>
    </div>
  );
}

export default DebugPanel;
