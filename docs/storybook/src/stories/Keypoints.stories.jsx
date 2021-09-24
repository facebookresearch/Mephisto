import React from "react";
import Wrapper from "./Wrapper";
import { Pose } from "@annotated/keypoint";
import "@annotated/keypoint/build/main.css";

export default {
  title: "Example/5. Keypoints [Prerelease]",
  decorators: [
    (Story) => (
      <Wrapper>
        <Story />
      </Wrapper>
    ),
  ],
};

export const Standalone = () => {
  const imageUrl =
    "https://cdn.vox-cdn.com/thumbor/jHceCkp8mUmqJh6-617m4u4_Rts=/1400x1400/filters:format(jpeg)/cdn.vox-cdn.com/uploads/chorus_asset/file/6080251/samsung-galaxy-mwc-2016-449.0.JPG";
  const imageHeight = 300;
  const imageWidth = 300;

  const hasHead = true;
  const hasLeftArm = true;
  const hasRightArm = true;
  const hasLeftFoot = true;
  const hasRightFoot = true;

  return (
    <div style={{ position: "relative", height: imageHeight }}>
      <div style={{ position: "absolute" }}>
        <img
          alt="pic of zuck on stage"
          src={imageUrl}
          style={{ height: imageHeight, width: imageWidth }}
        />
      </div>
      <div style={{ position: "absolute" }}>
        <Pose
          imageHeight={imageHeight}
          imageWidth={imageWidth}
          {...{
            hasHead,
            hasLeftArm,
            hasRightArm,
            hasLeftFoot,
            hasRightFoot,
          }}
        />
      </div>
    </div>
  );
};
