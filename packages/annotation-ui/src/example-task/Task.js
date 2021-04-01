import React from "react";
import { MenuItem } from "@blueprintjs/core";
import { useStore } from "../model";

import Layer from "../layers/Layer";
import VideoPlayer from "../layers/VideoPlayer";
import BBoxFrame from "../layers/BBoxFrame";

import { frameToMs, msToFrame, requestQueue } from "../helpers";

function VQALayers() {
  const { set, get, push } = useStore();

  React.useEffect(() => {
    set("selectedLayer", ["Query 1"]);
  }, []);

  const initData = get("initData");
  const taskData = get("taskData");

  if (!initData) {
    return null;
  }

  return (
    <>
      <Layer
        displayName="Video"
        icon="video"
        component={({ id }) => (
          <VideoPlayer
            fps={15}
            id={id}
            src={initData.src}
            width={initData.width}
            height={initData.height}
          />
        )}
        actions={
          <>
            <MenuItem
              icon="fast-backward"
              text="Rewind 5 seconds"
              onClick={() => {
                push(requestQueue("Video"), {
                  type: "rewind",
                  payload: 5,
                });
              }}
            />
            <MenuItem
              icon="fast-forward"
              text="Forward 5 seconds"
              onClick={() => {
                push(requestQueue("Video"), {
                  type: "ff",
                  payload: 5,
                });
              }}
            />
          </>
        }
        alwaysOn={true}
      />
      <VQALayerGroup
        queryNum={1}
        videoHeight={initData.height}
        videoWidth={initData.width}
        scale={initData.scale}
        data={taskData}
        videoFps={initData.fps}
      />
      <VQALayerGroup
        queryNum={2}
        videoHeight={initData.height}
        videoWidth={initData.width}
        scale={initData.scale}
        data={taskData}
        videoFps={initData.fps}
      />
      <VQALayerGroup
        queryNum={3}
        videoHeight={initData.height}
        videoWidth={initData.width}
        scale={initData.scale}
        data={taskData}
        videoFps={initData.fps}
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
  const { push } = useStore();

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
              push(requestQueue("Video"), {
                type: "seek",
                payload: frameToMs(visualCrop.frameNumber, videoFps) / 1000,
              });
              setTimeout(
                () =>
                  push(requestQueue("Video"), {
                    type: "screenshot",
                    payload: {
                      // TODO: have "screenshot" cmd work with the time property below
                      // so we can avoid having to do a seek as done above
                      time: frameToMs(visualCrop.frameNumber, videoFps) / 1000, // doesn't do anything right now
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
              push(requestQueue("Video"), {
                type: "seek",
                payload: frameToMs(queryFrame.frameNumber, videoFps) / 1000,
              });
            }}
          />
          <MenuItem
            icon="circle-arrow-right"
            text="Jump to response track start"
            onClick={() => {
              push(requestQueue("Video"), {
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
