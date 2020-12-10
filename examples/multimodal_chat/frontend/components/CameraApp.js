/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";
import Scene from "./Scene";

function posEqual(pos1, pos2) {
  if (!pos1 || !pos2) {
    return false;
  }
  for (let x = 0; x < 3; x++) {
    if (pos1[x] != pos2[x]) {
      return false;
    }
  }
  return true;
}

function CameraApp({ onUpdateScenePos, currentPosition, canControlScene }) {
  const [pos, setPos] = React.useState(undefined);
  const [savedPos, setSavedPos] = React.useState(undefined);
  const sceneRef = React.useRef();

  React.useEffect(() => {
    if (currentPosition !== undefined && sceneRef.current && !canControlScene) {
      sceneRef.current.updateCamera(...currentPosition);
    }
  }, [currentPosition]);

  return (
    <div>
      <button
        onClick={() => sceneRef.current && sceneRef.current.updateCamera()}
      >
        Reset to Origin
      </button>
      <button onClick={() => setSavedPos(pos)}>Save Current Position</button>
      <button
        disabled={!savedPos}
        onClick={() =>
          sceneRef.current && sceneRef.current.updateCamera(...savedPos)
        }
      >
        Reload Last Saved Position
      </button>
      <Scene
        ref={sceneRef}
        cameraPosition={pos}
        disableControls={!canControlScene}
        onPositionUpdate={(...args) => {
          setPos(args);
          if (!posEqual(args, currentPosition) && canControlScene) {
            onUpdateScenePos(args);
          }
        }}
        height={450}
        width={700}
      />
    </div>
  );
}

export default CameraApp;
