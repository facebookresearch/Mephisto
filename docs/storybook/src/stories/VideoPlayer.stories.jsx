import React from "react";
import Wrapper from "./Wrapper";

import {
  AppShell,
  Layer,
  VideoPlayer,
  requestsPathFor,
} from "annotation-toolkit";
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

export const Simple = () => (
  // TODO: Fix empty container showing when alwaysOn
  <AppShell
    layers={() => (
      <Layer
        alwaysOn
        displayName="Video"
        icon="video"
        component={() => <VideoPlayer src={VIDEO_URL} scale={0.5} />}
      />
    )}
  />
);

export const SimpleWithActions = () => {
  // TODO: actions only seem to show up when alwaysOn, investigate why
  const { push } = useStore();
  const FPS = 30;
  return (
    <AppShell
      layers={() => (
        <Layer
          alwaysOn
          displayName="Video"
          icon="video"
          component={() => <VideoPlayer src={VIDEO_URL} scale={0.5} />}
          actions={() => (
            <MenuItem
              text="Forward 5 frames"
              icon="step-forward"
              onClick={() => {
                push(requestsPathFor("Video"), {
                  type: "ff",
                  payload: 5 / FPS,
                });
              }}
            />
          )}
        />
      )}
    />
  );
};
