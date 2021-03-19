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
  if (selectedViewName) {
    const key = selectedViewName.join("|");
    const selectedLayer = get(["layers", key]);
    if (selectedLayer.component && !selectedLayer.alwaysOn) {
      SelectedViewComponent = () => (
        <selectedLayer.component id={selectedLayer.id} />
      );
    }
  }

  return (
    <>
      <div style={{ position: "absolute", zIndex: 12 }}>
        <SelectedViewComponent />
      </div>
      {alwaysOnLayers.map((layer) => (
        <div key={layer.id} style={{ zIndex: 10 }}>
          <layer.component id={layer.id} />
        </div>
      ))}
    </>
  );
}

export default ContentPanel;
