import React, { useContext, useEffect, useCallback, useRef } from "react";
import ReactPlayer from "react-player";
import { Context } from "../model/Store";

export default function VideoPlayer({ id }) {
  const { state, set, get, invoke } = useContext(Context);
  const vidRef = useRef();

  const process = useCallback(
    (req) => {
      if (req.type === "seek") {
        vidRef.current.seekTo(req.payload, "seconds");
      }
    },
    [vidRef.current]
  );

  const path = (...args) => ["layers", id, "data", ...args];

  // TODO: encapsulate process queue logic into a Hook or such so other
  // layer can also leverage it easily
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
        width={state.init.vidWidth}
        height={state.init.vidHeight}
        url={state.init.srcVideo}
        ref={vidRef}
        controls={true}
        progressInterval={300}
        onProgress={(progress) => {
          set(path("playedSeconds"), progress.playedSeconds);
        }}
        onDuration={(duration) => set(path("duration"), duration)}
        onSeek={() => {}}
      />
    </div>
  );
}
