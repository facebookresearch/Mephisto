import React from "react";
import { useStore } from "global-context-store";

import { Tabs, Tab } from "@blueprintjs/core";
const Inspector = require("react-json-inspector");
import "./DebugPanel.css";
import mapValues from "lodash.mapvalues";
import { isFunction } from "../utils";

function DebugPanel() {
  const { state: fullState } = useStore();
  const { __debug, _unsafe, ...state } = fullState;

  let displayState = null;
  try {
    const { layers, ...remainder } = state;
    displayState = {
      ...remainder,
      layers: mapValues(layers, (layer) => {
        const { config, ...rest } = layer;
        return {
          ...rest,
          config: mapValues(config, (value, key) => {
            if (["actions", "component"].indexOf(key) >= 0)
              // actions causes the browser to hang and component is too verbose
              return "HIDDEN";
            else if (isFunction(value)) return "fn()";
            else return value;
          }),
        };
      }),
    };
    // displayState = state;
  } catch {}

  const actionsFired = __debug?.actionsFired || [];

  return (
    <div style={{ height: "50%" }}>
      <div
        style={{ height: "100%" }}
        className="debug-panel bp3-menu bp3-elevation-1"
      >
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
              <div style={{ overflowY: "auto", height: "100%" }}>
                <Inspector
                  data={displayState}
                  isExpanded={(keypath) => !keypath.endsWith("config")}
                  filterOptions={{ ignoreCase: true }}
                />
              </div>
              // <code style={{ fontSize: 12 }}>
              //   {JSON.stringify(displayState, null, 2)}
              // </code>
            }
          />
          <Tab
            id="actions"
            title="Actions fired"
            panel={
              <div style={{ overflowY: "auto", height: "100%" }}>
                {/* TODO: The below on-the-fly reverse is probably not performant */}
                {[...actionsFired].reverse().map((a, idx) =>
                  a.type === "SET" ? (
                    <span
                      style={{ margin: 1 }}
                      className="bp3-tag bp3-minimal bp3-interactive"
                      title={a.payload.value}
                      key={idx}
                    >
                      {a.type[0]}{" "}
                      {Array.isArray(a.payload.key)
                        ? a.payload.key.join(".")
                        : a.payload.key}
                    </span>
                  ) : a.type === "INVOKE" ? (
                    <span
                      style={{ margin: 1 }}
                      className="bp3-tag bp3-minimal bp3-interactive"
                      key={idx}
                    >
                      {a.type[0]}{" "}
                      {Array.isArray(a.payload.path)
                        ? a.payload.path.join(".")
                        : a.payload.path}
                    </span>
                  ) : (
                    <span
                      style={{ margin: 1 }}
                      className="bp3-tag bp3-minimal bp3-interactive"
                      title={a.payload.value}
                      key={idx}
                    >
                      {a.type}
                    </span>
                  )
                )}
              </div>
            }
          />
        </Tabs>
      </div>
    </div>
  );
}

export default DebugPanel;
