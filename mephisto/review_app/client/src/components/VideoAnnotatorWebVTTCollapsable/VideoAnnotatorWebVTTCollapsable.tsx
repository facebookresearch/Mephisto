/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import CollapsableBlock from "components/CollapsableBlock/CollapsableBlock";
import * as React from "react";
import "./VideoAnnotatorWebVTTCollapsable.css";

type VideoAnnotatorWebVTTCollapsablePropsType = {
  data: string;
  open?: boolean;
};

function VideoAnnotatorWebVTTCollapsable(
  props: VideoAnnotatorWebVTTCollapsablePropsType
) {
  const { data, open } = props;

  return (
    <CollapsableBlock
      className={"video-annotator-webvtt"}
      open={open}
      title={"Tracks content (WebVTT)"}
      tooltip={"Tracks converted into WebVTT format"}
    >
      <pre>
        <code>{data}</code>
      </pre>
    </CollapsableBlock>
  );
}

export default VideoAnnotatorWebVTTCollapsable;
