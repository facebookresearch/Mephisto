import React from "react";

// a single frame bounding box for a VideoPlayer
function BBoxFrame() {
  const canvasRef = React.useRef();

  return (
    <div>
      Bounding Box
      <canvas
        ref={canvasRef}
        width={480 /*TODO: Retrieve from global state */}
        height={360 /*TODO: Retrieve from global state */}
        style={{ position: "absolute", left: 0, top: 0, pointerEvents: "none" }}
      ></canvas>
    </div>
  );
}

export default BBoxFrame;
