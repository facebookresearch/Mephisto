import React from "react";
import { useStore } from "../../model/Store";

// a single frame bounding box for a VideoPlayer
function BBoxFrame({
  displayWhen = () => false,
  getCoords,
  label = "",
  color = "red",
}) {
  const store = useStore();
  const { get } = store;

  const video = {
    height: get(["init", "vidHeight"]),
    width: get(["init", "vidWidth"]),
  };

  const LABEL_PADDING = 4;

  if (!displayWhen({ store })) {
    return null;
  }

  const [x, y, width, height] = getCoords({ store });

  const scale = 1;
  const rectX = scale * x;
  const rectY = scale * y;

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
        <rect
          x={rectX}
          y={rectY}
          width={scale * width}
          height={scale * height}
          style={{
            fill: "rgba(255,255,255,0.0)",
            strokeWidth: 2,
            stroke: color,
          }}
        />
        <text
          x={rectX - LABEL_PADDING}
          y={rectY - LABEL_PADDING}
          style={{
            fill: color,
          }}
        >
          {label}
        </text>
      </svg>
    </div>
  );
}

export default BBoxFrame;
