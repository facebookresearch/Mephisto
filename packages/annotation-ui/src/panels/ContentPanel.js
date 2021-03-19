import { AUTOMATIC_UPDATES } from "@blueprintjs/icons/lib/esm/generated/iconContents";
import React, { useContext } from "react";
import { Context } from "../model/Store";

function ContentPanel() {
  const { state, get } = useContext(Context);

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
          style={{ zIndex: 10 }}
          style={{ pointerEvents: layer.noPointerEvents ? "none" : "auto" }}
        >
          <layer.component id={layer.id} />
        </div>
      ))}
    </>
  );
}

export default ContentPanel;
