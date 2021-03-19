import React from "react";
import Layer from "./layers/Layer";
import VideoPlayer from "./layers/VideoPlayer";
import BBoxFrame from "./layers/VQA/BBoxFrame";

function Layers() {
  return (
    <div>
      <div className="bp3-tree">
        <ul className="bp3-tree-node-list bp3-tree-root">
          <Layer
            name="Video"
            icon="video"
            component={VideoPlayer}
            alwaysOn={true}
          />
          <Layer name="Query 1">
            <Layer
              name="Item Crop"
              icon="widget"
              component={BBoxFrame}
              noPointerEvents={true}
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
        </ul>
      </div>
    </div>
  );
}

export { Layers };
