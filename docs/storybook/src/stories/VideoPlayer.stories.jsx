import React from "react";
import Wrapper from "./Wrapper";

import { AppShell, Layer, VideoPlayer } from "annotation-toolkit";
import { useStore } from "global-context-store";
import { MenuItem } from "@blueprintjs/core";

const VIDEO_URL =
  "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4";

export default {
  title: "Example/3. Video Player",
  component: AppShell,
  decorators: [
    (Story) => (
      <Wrapper>
        <Story />
      </Wrapper>
    ),
  ],
};

export const Simple = () => {
  const { set } = useStore();
  React.useEffect(() => {
    set(["selectedLayer"], ["Video"]);
  }, [set]);
  return (
    <AppShell
      layers={() => (
        <Layer
          displayName="Video"
          icon="video"
          component={() => <VideoPlayer src={VIDEO_URL} scale={0.5} />}
          actions={
            <MenuItem
              text="Forward 5 frames"
              icon="step-forward"
              onClick={() => {}}
            />
          }
        />
      )}
    />
  );
};
