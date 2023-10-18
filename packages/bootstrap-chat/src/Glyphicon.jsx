/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";

function Glyphicon({ name }) {
  return (
    <div className="icon-container">
      <span className={`glyphicon glyphicon-${name}`} aria-hidden="true" />
    </div>
  );
}

export default Glyphicon;
