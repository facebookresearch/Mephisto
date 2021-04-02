import React from "react";
import { useStore } from "global-context-store";

// a single frame bounding box for a VideoPlayer
function BBoxFrame({
  displayWhen = () => true,
  getCoords,
  frameWidth,
  frameHeight,
  rectStyles = {},
  label = "",
  color = "red",
}) {
  const LABEL_PADDING = 4;

  const store = useStore();
  const coords = coords || getCoords({ store });

  if (!displayWhen({ store }) || !coords) {
    return null;
  }

  const [x, y, width, height] = coords;

  const scale = 1;
  const rectX = scale * x;
  const rectY = scale * y;

  console.log(scale * width - 4, "TEST");

  return (
    <div style={{ pointerEvents: "none" }}>
      <svg
        width={frameWidth}
        height={frameHeight}
        style={{
          // top: top - body.top,
          // left: left - body.left,
          pointerEvents: "none",
        }}
      >
        <rect
          x={rectX}
          y={rectY}
          width={scale * width - 4}
          height={scale * height - 4}
          style={{
            fill: "rgba(255,255,255,0.0)",
            strokeWidth: 2,
            stroke: color,
            ...rectStyles,
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
