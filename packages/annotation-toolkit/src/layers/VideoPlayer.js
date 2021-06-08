import React, { useContext, useEffect, useCallback, useRef } from "react";
import ReactPlayer from "react-player";
import { useStore } from "global-context-store";
import { Spinner } from "@blueprintjs/core";
import { dataPathBuilderFor, requestsPathFor } from "../helpers";
import { LayerContext } from "./Layer";

export default function VideoPlayer({
  id,
  src,
  fps = 30,
  scale,
  width,
  height,
  videoPlayerProps = {},
}) {
  const store = useStore();
  const { set, get } = store;
  const vidRef = useRef();
  const canvasRef = useRef();

  const layerInfo = useContext(LayerContext);
  id = id || layerInfo?.id || undefined;

  const [detectedSize, setDetectedSize] = React.useState([10, 10]);
  const [videoLoaded, setVideoLoaded] = React.useState(false);

  width = width || detectedSize[0] * scale;
  height = height || detectedSize[1] * scale;

  const process = useCallback(
    (req) => {
      if (req.type === "seek") {
        vidRef.current.seekTo(req.payload, "seconds");
      } else if (req.type === "rewind") {
        const currentTime = get(path("playedSeconds"));
        vidRef.current.seekTo(
          Math.max(currentTime - req.payload, 0),
          "seconds"
        );
      } else if (req.type === "ff") {
        const currentTime = get(path("playedSeconds"));
        const duration = get(path("duration"));
        vidRef.current.seekTo(
          Math.min(currentTime + req.payload, duration),
          "seconds"
        );
      } else if (req.type === "screenshot") {
        const [x, y, cropWidth, cropHeight] = req?.payload?.size || [
          0,
          0,
          width,
          height,
        ];
        canvasRef.current.height = cropHeight;
        canvasRef.current.width = cropWidth;
        canvasRef.current
          .getContext("2d")
          .drawImage(
            vidRef.current.getInternalPlayer(),
            x / scale,
            y / scale,
            cropWidth / scale,
            cropHeight / scale,
            0,
            0,
            cropWidth,
            cropHeight
          );
        const screenshotData = canvasRef.current.toDataURL("image/png");
        req.payload.callback({
          store,
          size: [x, y, cropWidth, cropHeight],
          data: screenshotData,
        });
      }
    },
    [vidRef.current]
  );

  React.useEffect(() => {
    /* Determine video dimensions */
    if (!videoLoaded) return;
    if (!vidRef.current.getInternalPlayer()) return;
    const videoWidth = vidRef.current.getInternalPlayer().videoWidth;
    const videoHeight = vidRef.current.getInternalPlayer().videoHeight;
    set(path("detectedSize"), [videoWidth, videoHeight]);
    setDetectedSize([videoWidth, videoHeight]);
  }, [vidRef.current, set, videoLoaded]);

  const path = dataPathBuilderFor(id);
  const requestsPath = requestsPathFor(id);

  // TODO: encapsulate process queue logic into a Hook or such so other
  // layers can also leverage it easily
  const requestQueue = get(requestsPath);
  useEffect(() => {
    if (!requestQueue || requestQueue.length === 0) return;
    requestQueue.forEach((request) => {
      process(request);
    });
    set(requestsPath, []);
  }, [requestQueue]);

  if (!src) return null;

  const {
    config: configProps = {},
    style: styleProps = {},
    ...restProps
  } = videoPlayerProps;

  return (
    <div style={{ position: "relative" }}>
      {!videoLoaded ? (
        <div
          className="loading-placeholder"
          style={{
            width: 300,
            height: 200,
          }}
        >
          <Spinner />
          <div style={{ marginTop: 20 }}>Loading video...</div>
        </div>
      ) : null}
      <ReactPlayer
        config={{
          ...configProps,
          file: {
            attributes: {
              crossOrigin: "true",
            },
          },
        }}
        style={{
          ...styleProps,
          visibility: videoLoaded ? "visible" : "hidden",
          opacity: videoLoaded ? 1 : 0,
          transition: "0.4s opacity",
        }}
        {...restProps}
        width={width}
        height={height}
        url={src}
        ref={vidRef}
        controls={true}
        progressInterval={1000 / fps}
        onProgress={(progress) => {
          set(path("playedSeconds"), progress.playedSeconds);
        }}
        onDuration={(duration) => {
          setVideoLoaded(true);
          set(path("duration"), duration);
        }}
        onSeek={() => {}}
        onPlay={() => set(path("playing"), true)}
        onPause={() => set(path("playing"), false)}
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
