import React from "react";
import { useStore } from "global-context-store";

import { Tabs, Tab } from "@blueprintjs/core";

function DebugPanel() {
  const { state: fullState } = useStore();
  const { __debug, ...state } = fullState;

  let displayState = null;
  try {
    displayState = Object.keys(state);
  } catch {}

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
                {(state.__debug?.actionsFired || []).map((a, idx) => (
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
