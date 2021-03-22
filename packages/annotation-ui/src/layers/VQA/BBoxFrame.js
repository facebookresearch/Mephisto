import React from "react";
import { useStore } from "../../model/Store";

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
  const store = useStore();
  const { get } = store;

  const LABEL_PADDING = 4;

  const coords = getCoords({ store });

  if (!displayWhen({ store }) || !coords) {
    return null;
  }

  const [x, y, width, height] = coords;

  const scale = 1;
  const rectX = scale * x;
  const rectY = scale * y;

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
          width={scale * width}
          height={scale * height}
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
