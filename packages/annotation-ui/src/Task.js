import React from "react";
import Layer from "./layers/Layer";
import VideoPlayer from "./layers/VideoPlayer";
import BBoxFrame from "./layers/VQA/BBoxFrame";
import { MenuItem } from "@blueprintjs/core";
import { useStore } from "./model/Store";

function VQALayers() {
  const { state, sendRequest } = useStore();

  const sampleQueryPayload = {
    itemCropTime: 4,
    queryFrameTime: 8,
  };

  return (
    <>
      <Layer
        displayName="Video"
        icon="video"
        component={({ id }) => (
          <VideoPlayer fps={16} id={id} src={state.init.srcVideo} />
        )}
        alwaysOn={true}
      />
      <Layer
        displayName="Query 1"
        actions={
          <>
            <MenuItem
              icon="circle-arrow-right"
              text="Jump to item crop"
              onClick={() => {
                sendRequest("Video", {
                  type: "seek",
                  payload: sampleQueryPayload.itemCropTime,
                });
              }}
            />
            <MenuItem
              icon="circle-arrow-right"
              text="Jump to query frame"
              onClick={() => {
                sendRequest("Video", {
                  type: "seek",
                  payload: sampleQueryPayload.queryFrameTime,
                });
              }}
            />
          </>
        }
      >
        <Layer
          displayName="Item Crop"
          icon="widget"
          component={(props) => (
            <BBoxFrame
              label="Item Crop"
              color="white"
              frameHeight={state.init.vidHeight}
              frameWidth={state.init.vidWidth}
              getCoords={() => [200, 20, 100, 100]}
              displayWhen={({ store }) => {
                const currentFrame = store.get(
                  "layers.Video.data.playedSeconds"
                );
                const timePoint = sampleQueryPayload.itemCropTime;
                return (
                  currentFrame > timePoint - 0.5 &&
                  currentFrame < timePoint + 0.5
                );
              }}
            />
          )}
          noPointerEvents={true}
          alwaysOn={true}
        />
        <Layer
          displayName="Response Track"
          icon="path-search"
          component={() => (
            <BBoxFrame
              frameHeight={state.init.vidHeight}
              frameWidth={state.init.vidWidth}
              label="Response Track"
              getCoords={({ store }) => {
                const currentFrame = store.get(
                  "layers.Video.data.playedSeconds"
                );
                return [200 + currentFrame * 30, 50, 100, 100];
              }}
            />
          )}
          noPointerEvents={true}
          alwaysOn={true}
        />
        <Layer
          displayName="Query Frame"
          icon="help"
          component={() => (
            <BBoxFrame
              frameHeight={state.init.vidHeight}
              frameWidth={state.init.vidWidth}
              rectStyles={{ fill: "rgba(255,0,0,0.4)" }}
              getCoords={() => [
                0,
                0,
                state.init.vidWidth,
                state.init.vidHeight,
              ]}
              displayWhen={({ store }) => {
                const currentFrame = store.get(
                  "layers.Video.data.playedSeconds"
                );
                const timePoint = sampleQueryPayload.queryFrameTime;
                return (
                  currentFrame > timePoint - 0.2 &&
                  currentFrame < timePoint + 0.2
                );
              }}
            />
          )}
          noPointerEvents={true}
          alwaysOn={true}
        />
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
