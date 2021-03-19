import React from "react";
import { useStore } from "../../model/Store";

// a single frame bounding box for a VideoPlayer
function BBoxFrame() {
  const { get } = useStore();

  // TODO: Retrieve from video state:
  const video = {
    height: 360,
    width: 480,
  };

  const kLabelPadding = 4;

  // TODO: Retrieve from task state:
  const frame = {
    x: 205.33,
    y: 0,
    width: 173.33,
    height: 192,
    rotation: 0,
    original_width: 1920,
    original_height: 1080,
    label: "left_hand",
    tags: ["instance_1"],
    frameNumber: 0,
    timePoint: 3.4,
  };

  const currentFrame = get("layers.Video.data.playedSeconds");
  if (!(currentFrame > 4.62 && currentFrame < 5)) {
    return null;
  }

  const labelFrames = [frame];
  const scale = 1;

  return (
    <div style={{ pointerEvents: "none" }}>
      <svg
        width={video.width}
        height={video.height}
        style={{
          // top: top - body.top,
          // left: left - body.left,
          pointerEvents: "none",
        }}
      >
        {labelFrames.map((frame) => {
          // const scale = video.width / frame.original_width

          console.log(frame);

          const rectX = scale * frame.x;
          const rectY = scale * frame.y;
          const c = "red";

          return (
            <React.Fragment key={frame.label}>
              <rect
                x={rectX}
                y={rectY}
                width={scale * frame.width}
                height={scale * frame.height}
                style={{
                  fill: "rgba(255,255,255,0.0)",
                  strokeWidth: 2,
                  stroke: c,
                }}
              />
              <text
                x={rectX - kLabelPadding}
                y={rectY - kLabelPadding}
                style={{
                  fill: c,
                }}
              >
                {frame.label}
              </text>
            </React.Fragment>
          );
        })}
      </svg>
    </div>
  );
}

export default BBoxFrame;
