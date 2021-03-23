import React, { useContext } from "react";
import { Context } from "../model/Store";
import { Slider } from "@blueprintjs/core";
import { frameToMs } from "../helpers";

export default function ContextPanel() {
  const { state, get, sendRequest } = useContext(Context);

  const videoLayerData = get(["layers", "Video", "data"]);
  const videoLoaded = !!videoLayerData;

  const selectedQuery = state.selectedLayer[0].replace("Query ", "");
  console.log(selectedQuery);

  let crop, importantFrames;
  if (videoLoaded && selectedQuery) {
    const query = state.taskData["query_set_" + selectedQuery];
    crop = query.visual_crop[0];

    const responseFrames = query.response_track.reduce((acc, val) => {
      acc[val.frameNumber] = val;
      return acc;
    }, {});

    const firstResponseFrameNum = Math.min(...Object.keys(responseFrames));
    const lastResponseFrameNum = Math.max(...Object.keys(responseFrames));

    importantFrames = [
      query.visual_crop[0].frameNumber,
      query.query_frame[0].frameNumber,
      firstResponseFrameNum,
      // lastResponseFrameNum
    ];
    importantFrames = importantFrames
      .map((f) => frameToMs(f, 5))
      .map((d) => d / 1000);

    console.log(importantFrames);
  }

  return videoLoaded ? (
    <div>
      Current video time (seconds): <span>{videoLayerData.playedSeconds}</span>
      <div style={{ padding: 20 }}>
        <Slider
          min={0}
          max={videoLayerData.duration}
          stepSize={0.1}
          labelValues={[
            0,
            // videoLayerData.duration / 4,
            // (videoLayerData.duration * 2) / 4,
            // (videoLayerData.duration * 3) / 4,
            videoLayerData.duration,
            ...importantFrames,
          ]}
          labelRenderer={(val) => {
            const label =
              val === importantFrames[0] ? (
                <span>
                  ↑<br />V
                </span>
              ) : val === importantFrames[1] ? (
                <span>
                  ↑<br />Q
                </span>
              ) : val === importantFrames[2] ? (
                <span>
                  ↑<br />R
                </span>
              ) : null;
            const mmss = new Date(val * 1000)
              .toISOString()
              .substr(14, 5)
              .replace("00:", ":");
            return label ? <span>{label}</span> : mmss;
          }}
          onChange={(value) => {
            sendRequest("Video", { type: "seek", payload: value });
          }}
          value={videoLayerData.playedSeconds}
          vertical={false}
        />
        {/* {state.screenshot?.data &&
        state.screenshot.query.toString() === selectedQuery ? (
          <div
            key={selectedQuery}
            style={{
              backgroundImage: "url(" + state.screenshot.data + ")",
              backgroundPosition:
                Math.round(-1 * crop.x * state.video.scale) +
                "px " +
                Math.round(-1 * crop.y * state.video.scale) +
                "px",
              height: crop.height * state.video.scale,
              width: crop.width * state.video.scale,
            }}
          />
        ) : null} */}
      </div>
    </div>
  ) : null;
}
