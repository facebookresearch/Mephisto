import React, { useContext } from "react";
import { useStore } from "global-context-store";

import { Menu, MenuDivider, Classes } from "@blueprintjs/core";

function isFunction(functionToCheck) {
  return (
    functionToCheck && {}.toString.call(functionToCheck) === "[object Function]"
  );
}

function ContentPanel() {
  const store = useStore();
  const { state, get } = store;

  const isGroup = (layer, otherLayer) => {
    if (!layer || !otherLayer) return false;
    const parent = layer.slice(0, -1);
    const otherParent = otherLayer.slice(0, -1);
    if (otherLayer.join("|") === parent.join("|")) return true;
    if (otherParent.join("|") === parent.join("|")) return true;
    return false;
  };

  const layers = get(["layers"]);
  if (!layers) return null;
  const alwaysOnLayers = Object.values(layers).filter((layer) => {
    return (
      layer.alwaysOn === true ||
      (isFunction(layer.alwaysOn) && layer.alwaysOn())
    );
  });
  const groupedLayers = Object.values(layers).filter((layer) => {
    return (
      layer.onWithGroup === true &&
      isGroup(layer.id.split("|"), state.selectedLayer)
    );
  });

  let Noop = () => null;

  let SelectedViewComponent = Noop;
  const selectedViewName = state.selectedLayer || null;
  let selectedLayer;
  if (selectedViewName) {
    const key = selectedViewName.join("|");
    selectedLayer = get(["layers", key]);
    if (
      selectedLayer?.component &&
      !selectedLayer.alwaysOn &&
      groupedLayers.indexOf(selectedLayer) < 0
    ) {
      SelectedViewComponent = selectedLayer.component;
    }
  }

  function gatherActions() {
    if (!state.selectedLayer) return { actions: [], path: [] };
    return state.selectedLayer.reduce(
      (acc, value) => {
        const path = [...acc.path, value];
        const component = get(["layers", path.join("|")]);
        if (!component) return acc;
        const actions = component.actions
          ? [...acc.actions, component.actions]
          : acc.actions;
        const actionPaths = component.actions
          ? [...acc.actionPaths, path.join(" / ")]
          : acc.actionPaths;
        return { actions, path, actionPaths };
      },
      { actions: [], path: [], actionPaths: [] }
    );
  }

  const gatheredActions = gatherActions();

  return (
    <>
      {selectedLayer ? (
        <div
          key={selectedLayer.id}
          style={{
            position: "absolute",
            zIndex: 12,
            pointerEvents: selectedLayer.noPointerEvents ? "none" : "auto",
          }}
        >
          <SelectedViewComponent
            id={selectedLayer.id}
            {...selectedLayer.getData({ store })}
          />
        </div>
      ) : null}
      {[...alwaysOnLayers, ...groupedLayers].map((layer) =>
        false ? null : (
          <div
            key={layer.id}
            style={{
              position: "absolute",
              zIndex: 10,
              pointerEvents: layer.noPointerEvents ? "none" : "auto",
            }}
          >
            <layer.component id={layer.id} {...layer.getData({ store })} />
          </div>
        )
      )}
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
          <Menu
            className={Classes.ELEVATION_1 + " pop"}
            key={gatheredActions.actionPaths.join("//")}
          >
            {alwaysOnLayers.map((layer, idx) => (
              <React.Fragment key={idx}>
                <MenuDivider title={layer.id} />
                {layer.actions}
              </React.Fragment>
            ))}
            {gatheredActions.actions.length === 0 ? (
              <MenuDivider
                icon={"layer"}
                title={state.selectedLayer.join(" / ")}
              />
            ) : null}
            {gatheredActions.actions.map((action, idx) => (
              <React.Fragment key={idx}>
                <MenuDivider title={gatheredActions.actionPaths[idx]} />
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
