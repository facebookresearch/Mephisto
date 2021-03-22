import React from "react";
import Layer from "./layers/Layer";
import VideoPlayer from "./layers/VideoPlayer";
import BBoxFrame from "./layers/VQA/BBoxFrame";
import { MenuItem } from "@blueprintjs/core";
import { useStore } from "./model/Store";

function VQALayers() {
  const { sendRequest } = useStore();
  return (
    <>
      <Layer
        displayName="Video"
        icon="video"
        component={(props) => <VideoPlayer {...props} />}
        alwaysOn={true}
      />
      <Layer
        displayName="Query 1"
        actions={
          <MenuItem
            icon="circle-arrow-right"
            text="Jump to item crop"
            onClick={() => {
              sendRequest("Video", { type: "seek", payload: 4 });
            }}
          />
        }
      >
        <Layer
          displayName="Item Crop"
          icon="widget"
          component={(props) => <BBoxFrame {...props} />}
          noPointerEvents={true}
          alwaysOn={true}
        />
        <Layer displayName="Response Track" icon="path-search" />
        <Layer displayName="Query Frame" icon="help" />
      </Layer>
      <Layer displayName="Query 2">
        <Layer displayName="Item Crop" icon="widget" />
        <Layer displayName="Response Track" icon="path-search" />
        <Layer displayName="Query Frame" icon="help" />
      </Layer>
      <Layer displayName="Query 3">
        <Layer displayName="Item Crop" icon="widget" />
        <Layer displayName="Response Track" icon="path-search" />
        <Layer displayName="Query Frame" icon="help" />
      </Layer>
    </>
  );
}

function NarrationLayers() {
  return <Layer displayName="Joe" icon="person" />;
}

export { VQALayers as Layers };
