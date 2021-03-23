import React, { useContext, useEffect, useCallback, useRef } from "react";
import ReactPlayer from "react-player";
import { useStore } from "../model/Store";

export default function VideoPlayer({ id, src, fps = 30, width, height }) {
  const store = useStore();
  const { state, set, get } = store;
  const vidRef = useRef();
  const canvasRef = useRef();

  const process = useCallback(
    (req) => {
      if (req.type === "seek") {
        vidRef.current.seekTo(req.payload, "seconds");
      } else if (req.type === "screenshot") {
        console.log(vidRef.current.getInternalPlayer());
        canvasRef.current
          .getContext("2d")
          .drawImage(vidRef.current.getInternalPlayer(), 0, 0, width, height);
        const screenshotData = canvasRef.current.toDataURL("image/png");
        req.payload({ store, data: screenshotData });
      }
    },
    [vidRef.current]
  );

  const path = (...args) => ["layers", id, "data", ...args];

  // TODO: encapsulate process queue logic into a Hook or such so other
  // layers can also leverage it easily
  const requestQueue = get(path("requests"));
  useEffect(() => {
    if (!requestQueue || requestQueue.length === 0) return;
    requestQueue.forEach((request) => {
      process(request);
    });
    set(path("requests"), []);
  }, [requestQueue]);

  if (!state.init.srcVideo) return null;

  return (
    <div style={{ position: "relative" }}>
      <ReactPlayer
        config={{
          file: {
            attributes: {
              crossOrigin: "true",
            },
          },
        }}
        width={width}
        height={height}
        url={src}
        ref={vidRef}
        controls={true}
        progressInterval={1000 / fps}
        onProgress={(progress) => {
          set(path("playedSeconds"), progress.playedSeconds);
        }}
        onDuration={(duration) => set(path("duration"), duration)}
        onSeek={() => {}}
      />
      <canvas
        style={{ visibility: "hidden" }}
        height={height}
        width={width}
        ref={canvasRef}
      ></canvas>
    </div>
  );
}
