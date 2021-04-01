import React from "react";
import ReactDOM from "react-dom";
import "./index.css";
import AppShell from "./AppShell";
import DataLoader from "./example-task/DataLoader";
import Store from "./model";
import { Layers } from "./example-task/Task";

import "react-mosaic-component/react-mosaic-component.css";
import "@blueprintjs/core/lib/css/blueprint.css";
import "@blueprintjs/icons/lib/css/blueprint-icons.css";

ReactDOM.render(
  <React.StrictMode>
    <Store>
      <DataLoader />
      <AppShell layers={() => <Layers />} />
    </Store>
  </React.StrictMode>,
  document.getElementById("app")
);
