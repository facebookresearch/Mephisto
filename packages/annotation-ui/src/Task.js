import React from "react";
import Layer from "./layers/Layer";
import VideoPlayer from "./layers/VideoPlayer";
import BBoxFrame from "./layers/VQA/BBoxFrame";
import { MenuItem } from "@blueprintjs/core";
import { useStore } from "./model/Store";

function Layers() {
  const { sendRequest } = useStore();
  return (
    <>
      <Layer
        name="Video"
        icon="video"
        component={VideoPlayer}
        alwaysOn={true}
      />
      <Layer
        name="Query 1"
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
          name="Item Crop"
          icon="widget"
          component={BBoxFrame}
          noPointerEvents={true}
          alwaysOn={true}
        />
        <Layer name="Response Track" icon="path-search" />
        <Layer name="Query Frame" icon="help" />
      </Layer>
      <Layer name="Query 2">
        <Layer name="Item Crop" icon="widget" />
        <Layer name="Response Track" icon="path-search" />
        <Layer name="Query Frame" icon="help" />
      </Layer>
      <Layer name="Query 3">
        <Layer name="Item Crop" icon="widget" />
        <Layer name="Response Track" icon="path-search" />
        <Layer name="Query Frame" icon="help" />
      </Layer>
    </>
  );
}

export { Layers };
