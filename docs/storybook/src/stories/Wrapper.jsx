/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";

import "@annotated/shell/build/main.css";
import "@blueprintjs/core/lib/css/blueprint.css";
import { Helmet } from "react-helmet";
import Store from "global-context-store";

export default function Wrapper({ children }) {
  return (
    <div style={{ height: "calc(100vh - 30px)" }}>
      <Helmet>
        <link
          rel="stylesheet"
          href="https://unpkg.com/@blueprintjs/icons@3.26.0/lib/css/blueprint-icons.css"
        />
      </Helmet>
      <Store>{children}</Store>
    </div>
  );
}
