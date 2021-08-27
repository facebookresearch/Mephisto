import React, { useContext } from "react";
import { useStore } from "global-context-store";
import { isFunction } from "../utils";
import mapValues from "lodash.mapvalues";

import { Menu, MenuDivider, Classes, Card } from "@blueprintjs/core";
import { LayerContext } from "../layers/Layer";

function ContentPanel({ instructionPane: InstructionPane }) {
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

  let layers = get(["layers"]);
  if (!layers) return null;
  layers = mapValues(layers, (layer) => layer.config);
  const alwaysOnLayers = Object.entries(layers)
    .filter(([layerName, layer]) => {
      if (!layer) {
        throw new Error(
          `Could not find any Layer registered with id: "${layerName}"`
        );
      }
      return (
        layer.alwaysOn === true ||
        (isFunction(layer.alwaysOn) && layer.alwaysOn())
      );
    })
    .map(([_, layer]) => layer);
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
    selectedLayer = get(["layers", key, "config"]);
    if (
      selectedLayer?.component &&
      !selectedLayer.alwaysOn &&
      groupedLayers.indexOf(selectedLayer) < 0
    ) {
      SelectedViewComponent = selectedLayer.component;
    }
  }

  function gatherActions() {
    if (!state.selectedLayer) return { actions: [], path: [], actionPaths: [] };
    return state.selectedLayer.reduce(
      (acc, value) => {
        const path = [...acc.path, value];
        const component = get(["layers", path.join("|"), "config"]);
        if (!component) return acc;
        const actions = component.actions
          ? [...acc.actions, component.actions()]
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
          <LayerContext.Provider value={{ id: selectedLayer.id }}>
            <SelectedViewComponent
              id={selectedLayer.id}
              {...selectedLayer.getData({ store })}
            />
          </LayerContext.Provider>
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
            <LayerContext.Provider value={{ id: layer.id }}>
              <layer.component id={layer.id} {...layer.getData({ store })} />
            </LayerContext.Provider>
          </div>
        )
      )}
      {alwaysOnLayers.length > 0 || gatheredActions.length > 0 ? (
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
          {InstructionPane ? (
            <Card className="bp3-dark" style={{ marginBottom: 5, padding: 10 }}>
              <InstructionPane />
            </Card>
          ) : null}
          <Menu
            className={Classes.ELEVATION_1 + " pop"}
            key={gatheredActions.actionPaths.join("//")}
          >
            {alwaysOnLayers
              .filter((layer) => {
                if (layer.hideActionsIfUnselected) {
                  return false;
                }

                // don't show actions that will be shown by virtue of layer selection
                // to avoid duplications
                const layerPath = layer.id.replace("|", " / ");
                return gatheredActions.actionPaths.indexOf(layerPath) < 0;
              })
              .map((layer, idx) =>
                layer.actions ? (
                  <React.Fragment key={idx}>
                    <MenuDivider title={layer.id} />
                    {layer.actions()}
                  </React.Fragment>
                ) : null
              )}
            {/* If no gathered actions, just show the layer name: */}
            {gatheredActions.actions.length === 0 && state.selectedLayer ? (
              <MenuDivider
                icon={"layer"}
                title={
                  state.selectedLayer.join(" / ") +
                  " " +
                  String.fromCharCode(11049)
                }
              />
            ) : null}
            {gatheredActions.actions.map((action, idx) => (
              <React.Fragment key={idx}>
                <MenuDivider
                  title={
                    gatheredActions.actionPaths[idx] +
                    " " +
                    String.fromCharCode(11049)
                  }
                />
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
