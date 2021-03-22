import React from "react";
import ReactDOM from "react-dom";
import "./index.css";
import App from "./App";
import Store from "./model/Store";

import "react-mosaic-component/react-mosaic-component.css";
import "@blueprintjs/core/lib/css/blueprint.css";
import "@blueprintjs/icons/lib/css/blueprint-icons.css";

ReactDOM.render(
  <React.StrictMode>
    <Store>
      <App />
    </Store>
  </React.StrictMode>,
  document.getElementById("app")
);
