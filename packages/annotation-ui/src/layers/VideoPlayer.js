import React, { useContext, useEffect, useCallback } from "react";
import ReactPlayer from "react-player";
import { Context } from "../model/Store";

import { Menu, MenuItem, MenuDivider, Classes, Icon } from "@blueprintjs/core";

export default function VideoPlayer({ id }) {
  const { state, set, get } = useContext(Context);
  const vidRef = React.useRef();
  const canvasRef = React.useRef();

  const process = React.useCallback((req) => {
    if (req.type === "seek") {
      vidRef.current.seekTo(req.payload, "seconds");
    }
  });

  const path = (...args) => ["layers", id, "data", ...args];

  const requestQueue = get(path("requests"));
  React.useEffect(() => {
    if (!requestQueue || requestQueue.length === 0) return;
    requestQueue.forEach((request) => {
      console.log(
        "processing",
        request,
        requestQueue.filter((r) => r !== request)
      );
      process(request);
    });
    set(path("requests"), []);
  }, [requestQueue]);

  if (!state.srcVideo) return null;

  return (
    <div style={{ position: "relative" }}>
      <ReactPlayer
        width={480}
        height={360}
        url={state.srcVideo}
        ref={vidRef}
        controls={true}
        progressInterval={300}
        onProgress={(progress) => {
          set(path("playedSeconds"), progress.playedSeconds);
        }}
        onDuration={(duration) => set(path("duration"), duration)}
        onSeek={() => {}}
      />
      <canvas
        ref={canvasRef}
        width={480}
        height={360}
        style={{ position: "absolute", left: 0, top: 0, pointerEvents: "none" }}
      ></canvas>

      {state.selectedLayer ? (
        <div
          style={{
            marginRight: 10,
            marginTop: 10,
            position: "absolute",
            right: 0,
            top: 0,
          }}
        >
          <Menu className={Classes.ELEVATION_1}>
            <MenuDivider
              icon={"layer"}
              title={state.selectedLayer.join(" / ")}
            />
            {/* <MenuDivider />
          <MenuItem icon="new-object" text="Add keyframe" />
          <MenuItem icon="cross" text="Remove keyframe" />
          <MenuItem icon="predictive-analysis" text="Request model assistance" /> */}
            {/* <MenuDivider />
          <MenuItem icon="cog" labelElement={<Icon icon="share" />} text="Settings..." /> */}
          </Menu>
        </div>
      ) : null}
    </div>
  );
}
