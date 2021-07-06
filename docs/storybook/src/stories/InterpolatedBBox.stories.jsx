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

export const BasicBox = () => {
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
