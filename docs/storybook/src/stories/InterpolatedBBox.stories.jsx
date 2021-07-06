import React from "react";
import Wrapper from "./Wrapper";

import {
  AppShell,
  Layer,
  VideoPlayer,
  MovableRect,
  dataPathBuilderFor,
} from "annotation-toolkit";
import { useStore } from "global-context-store";
import { MenuItem } from "@blueprintjs/core";

const VIDEO_URL =
  "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4";

export default {
  title: "Example/4. Interpolated BBox",
  component: AppShell,
  decorators: [
    (Story) => (
      <Wrapper>
        <Story />
      </Wrapper>
    ),
  ],
};

export const Standalone = () => {
  const [frame, setFrame] = React.useState(0);

  return (
    <div style={{ padding: "15px 20px" }}>
      <h1>How interpolated bounding boxes work</h1>
      <h3>Current frame: {frame}</h3>
      <button
        onClick={() => {
          setFrame(frame + 1);
        }}
      >
        Next Frame
      </button>{" "}
      <button
        disabled={frame === 0}
        onClick={() => {
          setFrame(frame - 1);
        }}
      >
        Prev Frame
      </button>
      <MovableRect
        defaultBox={[50, 200, 100, 100]}
        getTs={() => {
          return frame;
        }}
      />
      <ul style={{ marginTop: 200, fontSize: 20 }}>
        <li>
          <strong>Red box: unselected box</strong>
        </li>
        <li>
          <strong>Light blue (cyan) box: selected box</strong>; selectable via
          mouse click
        </li>
        <li>
          <strong>Solid border: Keyframe</strong>; A keyframe is a frame that
          has a fixed position. A keyframe is auto-set whenever you drag or
          re-position any bounding box.
        </li>
        <li>
          <strong>Dashed border: Frame</strong>; A frame is a frame without a
          fixed position. Its position is based on its neighboring keyframes. A
          frame is interpolated, meaning that it intelligently adjusts so that
          there is smooth movement of the bounding box between its neighboring
          keyframes.
        </li>
      </ul>
    </div>
  );
};

export const SynchedWithVideoPlayer = () => {
  const store = useStore();
  const storeRef = React.useRef(store);
  React.useEffect(() => {
    storeRef.current = store;
  }, [store]);

  return (
    <AppShell
      showDebugPane={false}
      layers={() => (
        <>
          <Layer
            alwaysOn
            displayName="Video"
            icon="video"
            component={() => <VideoPlayer src={VIDEO_URL} scale={0.5} />}
          />
          <Layer
            alwaysOn
            displayName="BBox"
            icon="widget"
            component={({ id }) => (
              <MovableRect
                id={id}
                defaultBox={[10, 10, 100, 100]}
                getTs={() => {
                  const ps =
                    storeRef.current.state?.layers?.Video.data?.playedSeconds;
                  return ps;
                }}
              />
            )}
          />
        </>
      )}
    />
  );
};
