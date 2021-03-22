import React, { useContext } from "react";
import { Context } from "../model/Store";

import { Menu, MenuItem, MenuDivider, Classes } from "@blueprintjs/core";

function ContentPanel() {
  const { state, get, set, invoke } = useContext(Context);

  const layers = get(["layers"]);
  if (!layers) return null;
  const alwaysOnLayers = Object.values(layers).filter(
    (layer) => layer.alwaysOn
  );

  let Noop = () => null;

  let SelectedViewComponent = Noop;
  const selectedViewName = state.selectedLayer || null;
  let selectedLayer;
  if (selectedViewName) {
    const key = selectedViewName.join("|");
    selectedLayer = get(["layers", key]);
    if (selectedLayer.component && !selectedLayer.alwaysOn) {
      SelectedViewComponent = () => (
        <selectedLayer.component id={selectedLayer.id} />
      );
    }
  }

  function gatherActions() {
    if (!state.selectedLayer) return { actions: [], path: [] };
    return state.selectedLayer.reduce(
      (acc, value) => {
        const path = [...acc.path, value];
        const component = get(["layers", path.join("|")]);
        const actions = component.actions
          ? [...acc.actions, component.actions]
          : acc.actions;
        return { actions, path };
      },
      { actions: [], path: [] }
    );
  }

  const actions = gatherActions().actions;

  return (
    <>
      {selectedLayer ? (
        <div
          style={{
            position: "absolute",
            zIndex: 12,
            pointerEvents: selectedLayer.noPointerEvents ? "none" : "auto",
          }}
        >
          <SelectedViewComponent />
        </div>
      ) : null}
      {alwaysOnLayers.map((layer) => (
        <div
          key={layer.id}
          style={{
            position: "absolute",
            zIndex: 10,
            pointerEvents: layer.noPointerEvents ? "none" : "auto",
          }}
        >
          <layer.component id={layer.id} />
        </div>
      ))}
      {state.selectedLayer ? (
        <div
          style={{
            marginRight: 10,
            marginTop: 10,
            position: "absolute",
            right: 0,
            top: 0,
            zIndex: 100,
            minWidth: 200,
          }}
        >
          <Menu className={Classes.ELEVATION_1}>
            <MenuDivider
              icon={"layer"}
              title={state.selectedLayer.join(" / ")}
            />
            {actions.map((action, idx) => (
              <React.Fragment key={idx}>
                <MenuDivider />
                {action}
              </React.Fragment>
            ))}
          </Menu>
        </div>
      ) : null}
    </>
  );
}

export default ContentPanel;
