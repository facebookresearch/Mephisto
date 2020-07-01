/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";
import { Button } from "react-bootstrap";

import Slider from "rc-slider";
import "rc-slider/assets/index.css";

function VolumeControl(props) {
  const { volume, onVolumeChange } = props;
  const [showSlider, setShowSlider] = React.useState(false);

  let volume_control_style = {
    opacity: "1",
    fontSize: "11px",
    color: "white",
    float: "right",
    marginRight: "10px",
  };

  let slider_style = {
    height: 26,
    width: 150,
    marginRight: 14,
    float: "left",
  };

  if (showSlider) {
    return (
      <div style={volume_control_style}>
        <div style={slider_style}>
          <Slider
            onChange={(v) => onVolumeChange(v / 100)}
            style={{ marginTop: 10 }}
            defaultValue={volume * 100}
          />
        </div>
        <Button onClick={() => setShowSlider(false)}>
          <span
            style={{ marginRight: 5 }}
            className="glyphicon glyphicon-remove"
          />
          Hide Volume
        </Button>
      </div>
    );
  } else {
    return (
      <div style={volume_control_style}>
        <Button onClick={() => setShowSlider(true)}>
          <span
            className="glyphicon glyphicon glyphicon-volume-up"
            style={{ marginRight: 5 }}
            aria-hidden="true"
          />
          Volume
        </Button>
      </div>
    );
  }
}

export default VolumeControl;
