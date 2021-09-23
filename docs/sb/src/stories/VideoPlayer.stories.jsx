import React from "react";
import Wrapper from "./Wrapper";

import { AppShell, Layer, requestsPathFor } from "@annotated/shell";
import { VideoPlayer } from "@annotated/video-player";
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

export const Standalone = () => <VideoPlayer src={VIDEO_URL} scale={0.5} />;

export const InAppShell = () => (
  // TODO: Fix empty container showing when alwaysOn
  <AppShell
    layers={() => (
      <Layer
        alwaysOn
        displayName="Video"
        icon="video"
        component={({ id }) => (
          <VideoPlayer id={id} src={VIDEO_URL} scale={0.5} />
        )}
      />
    )}
  />
);

export const WithActions = () => {
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
          component={({ id }) => (
            <VideoPlayer id={id} src={VIDEO_URL} scale={0.5} />
          )}
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

export const WithScreenshots = () => {
  const store = useStore();
  const storeRef = React.useRef(store);
  // TODO: is there a more elegent way to reference global state rather than through a ref?
  React.useEffect(() => {
    storeRef.current = store;
  }, [store]);

  const { push, set } = store;
  const FPS = 30;
  return (
    <AppShell
      showDebugPane={false}
      contextPanel={() => (
        <img height={100} src={store.state?.screenshot?.data} />
      )}
      layers={() => (
        <Layer
          alwaysOn
          displayName="Video"
          icon="video"
          component={({ id }) => (
            <VideoPlayer id={id} src={VIDEO_URL} scale={0.5} />
          )}
          actions={() => (
            <MenuItem
              text="Capture Screenshot"
              icon="camera"
              onClick={() => {
                push(requestsPathFor("Video"), {
                  type: "screenshot",
                  payload: {
                    size: [
                      0,
                      0,
                      ...storeRef.current.state?.layers?.Video.data
                        ?.detectedSize,
                    ],
                    callback: (info) => {
                      storeRef.current.set(["screenshot"], info);
                    },
                  },
                });
              }}
            />
          )}
        />
      )}
    />
  );
};
