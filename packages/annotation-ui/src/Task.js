import React from "react";
import Layer from "./layers/Layer";
import VideoPlayer from "./layers/VideoPlayer";
import BBoxFrame from "./layers/VQA/BBoxFrame";
import { MenuItem } from "@blueprintjs/core";
import { useStore } from "./model/Store";

import vqaData from "./mock-data/vqa.json";
import groupBy from "lodash.groupby";
import mapValues from "lodash.mapvalues";

import { frameToMs, msToFrame } from "./helpers";

function VQALayers() {
  function prepareData(data) {
    let d = groupBy(data.payload, "label");
    d = mapValues(d, (val) => groupBy(val, "tags[0]"));
    return d;
  }

  const videoSrc =
    "https://interncache-ash.fbcdn.net/v/t53.39266-7/10000000_441474370388831_2571013882988688057_n.mp4?_nc_map=test-rt&ccb=1-3&_nc_sid=5f5f54&efg=eyJ1cmxnZW4iOiJwaHBfdXJsZ2VuX2NsaWVudC9pbnRlcm4vc2l0ZS94L2ZiY2RuIn0%3D&_nc_ht=interncache-ash&_nc_rmd=260&oh=f275d96ea09f486be0166da312f84127&oe=607E239D";

  const originalVideoWidth = 1920;
  const originalVideoHeight = 1440;
  const scale = 0.38;
  const videoWidth = originalVideoWidth * scale;
  const videoHeight = originalVideoHeight * scale;

  const data = prepareData(vqaData);

  return (
    <>
      <Layer
        displayName="Video"
        icon="video"
        component={({ id }) => (
          <VideoPlayer
            fps={16}
            id={id}
            src={videoSrc}
            width={videoWidth}
            height={videoHeight}
          />
        )}
        alwaysOn={true}
      />
      <VQALayerGroup
        queryNum={1}
        videoHeight={videoHeight}
        videoWidth={videoWidth}
        scale={scale}
        data={data}
      />
      <VQALayerGroup
        queryNum={2}
        videoHeight={videoHeight}
        videoWidth={videoWidth}
        scale={scale}
        data={data}
      />
      <VQALayerGroup
        queryNum={3}
        videoHeight={videoHeight}
        videoWidth={videoWidth}
        scale={scale}
        data={data}
      />
    </>
  );
}

function VQALayerGroup({ data, queryNum, videoHeight, videoWidth, scale }) {
  const { sendRequest } = useStore();

  const querySet = data["query_set_" + queryNum];
  const itemCrop = querySet.visual_crop[0];
  const queryFrame = querySet.query_frame[0];
  const responseTrack = querySet.response_track;

  const videoFps = 4;

  const responseFrames = responseTrack.reduce((acc, val) => {
    acc[val.frameNumber] = val;
    return acc;
  }, {});

  return (
    <Layer
      displayName={"Query " + queryNum}
      actions={
        <>
          <MenuItem
            icon="circle-arrow-right"
            text="Jump to item crop"
            onClick={() => {
              sendRequest("Video", {
                type: "seek",
                payload: frameToMs(itemCrop.frameNumber, videoFps) / 1000,
              });
            }}
          />
          <MenuItem
            icon="circle-arrow-right"
            text="Jump to query frame"
            onClick={() => {
              sendRequest("Video", {
                type: "seek",
                payload: frameToMs(queryFrame.frameNumber, videoFps) / 1000,
              });
            }}
          />
          <MenuItem
            icon="circle-arrow-right"
            text="Jump to response frame start"
            onClick={() => {
              const firstFrameNum = Math.min(...Object.keys(responseFrames));
              sendRequest("Video", {
                type: "seek",
                payload: frameToMs(firstFrameNum, videoFps) / 1000,
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
            label={`Item Crop #${queryNum}`}
            color="white"
            frameHeight={videoHeight}
            frameWidth={videoWidth}
            getCoords={() => [
              itemCrop.x * scale,
              itemCrop.y * scale,
              itemCrop.width * scale,
              itemCrop.height * scale,
            ]}
            displayWhen={({ store }) => {
              const currentFrame = store.get("layers.Video.data.playedSeconds");
              const timePoint =
                frameToMs(itemCrop.frameNumber, videoFps) / 1000;
              return (
                currentFrame > timePoint - 0.5 && currentFrame < timePoint + 0.5
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
            frameHeight={videoHeight}
            frameWidth={videoWidth}
            label={`Response Track #${queryNum}`}
            getCoords={({ store }) => {
              const currentTime =
                store.get("layers.Video.data.playedSeconds") || 0;
              const currentFrame = msToFrame(currentTime * 1000, videoFps);
              const inFrame = currentFrame in responseFrames;
              if (!inFrame) return null;
              const responseFrame = responseFrames[currentFrame];
              return [
                responseFrame.x * scale,
                responseFrame.y * scale,
                responseFrame.width * scale,
                responseFrame.height * scale,
              ];
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
            frameHeight={videoHeight}
            frameWidth={videoWidth}
            rectStyles={{ fill: "rgba(255,0,0,0.4)" }}
            getCoords={() => [
              queryFrame.x * scale,
              queryFrame.y * scale,
              queryFrame.width * scale,
              queryFrame.height * scale,
            ]}
            displayWhen={({ store }) => {
              const currentFrame = store.get("layers.Video.data.playedSeconds");
              const timePoint =
                frameToMs(queryFrame.frameNumber, videoFps) / 1000;
              return (
                currentFrame > timePoint - 0.2 && currentFrame < timePoint + 0.2
              );
            }}
          />
        )}
        noPointerEvents={true}
        alwaysOn={true}
      />
    </Layer>
  );
}

export { VQALayers as Layers };
