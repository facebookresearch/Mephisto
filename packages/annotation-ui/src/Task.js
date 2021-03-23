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
  const scale = 0.33;
  const videoWidth = originalVideoWidth * scale;
  const videoHeight = originalVideoHeight * scale;
  const videoFps = 5;

  const { set } = useStore();
  const data = prepareData(vqaData);

  React.useEffect(() => {
    set(["taskData"], data);
    set("video.scale", scale);
  }, [vqaData]);

  return (
    <>
      <Layer
        displayName="Video"
        icon="video"
        component={({ id }) => (
          <VideoPlayer
            fps={15}
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
        videoFps={videoFps}
      />
      <VQALayerGroup
        queryNum={2}
        videoHeight={videoHeight}
        videoWidth={videoWidth}
        scale={scale}
        data={data}
        videoFps={videoFps}
      />
      <VQALayerGroup
        queryNum={3}
        videoHeight={videoHeight}
        videoWidth={videoWidth}
        scale={scale}
        data={data}
        videoFps={videoFps}
      />
    </>
  );
}

function VQALayerGroup({
  data,
  queryNum,
  videoHeight,
  videoWidth,
  videoFps,
  scale,
}) {
  const { sendRequest } = useStore();

  const querySet = data["query_set_" + queryNum];
  const visualCrop = querySet.visual_crop[0];
  const queryFrame = querySet.query_frame[0];
  const responseTrack = querySet.response_track;

  const responseFrames = responseTrack.reduce((acc, val) => {
    acc[val.frameNumber] = val;
    return acc;
  }, {});

  const firstResponseFrameNum = Math.min(...Object.keys(responseFrames));

  return (
    <Layer
      displayName={"Query " + queryNum}
      actions={
        <>
          <MenuItem
            icon="circle-arrow-right"
            text="Jump to visual crop"
            onClick={() => {
              sendRequest("Video", {
                type: "seek",
                payload: frameToMs(visualCrop.frameNumber, videoFps) / 1000,
              });
              setTimeout(
                () =>
                  sendRequest("Video", {
                    type: "screenshot",
                    payload: {
                      // TODO: have "screenshot" cmd work with time property
                      // so we can avoid having to do a seek as done above
                      time: frameToMs(visualCrop.frameNumber, videoFps) / 1000,
                      callback: ({ store, data }) =>
                        store.set("screenshot", {
                          data: data,
                          query: queryNum,
                        }),
                    },
                  }),
                600
              );
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
            text="Jump to response track start"
            onClick={() => {
              sendRequest("Video", {
                type: "seek",
                payload: frameToMs(firstResponseFrameNum, videoFps) / 1000,
              });
            }}
          />
        </>
      }
    >
      <Layer
        displayName="Visual Crop"
        icon="widget"
        component={(props) => (
          <BBoxFrame
            label={`Visual Crop #${queryNum}`}
            color="white"
            frameHeight={videoHeight}
            frameWidth={videoWidth}
            getCoords={() => [
              visualCrop.x * scale,
              visualCrop.y * scale,
              visualCrop.width * scale,
              visualCrop.height * scale,
            ]}
            displayWhen={({ store }) => {
              const currentFrame = store.get("layers.Video.data.playedSeconds");
              const timePoint =
                frameToMs(visualCrop.frameNumber, videoFps) / 1000;
              return (
                currentFrame > timePoint - 0.2 && currentFrame < timePoint + 0.2
              );
            }}
          />
        )}
        noPointerEvents={true}
        onWithGroup={true}
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
        onWithGroup={true}
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
        onWithGroup={true}
      />
    </Layer>
  );
}

export { VQALayers as Layers };
