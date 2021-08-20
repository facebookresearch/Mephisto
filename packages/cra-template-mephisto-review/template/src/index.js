import React from "react";
import ReactDOM from "react-dom";
import "./index.css";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
import AllItemView from "./components/AllItemView";
import ItemView from "./components/ItemView";
import "normalize.css/normalize.css";
import "@blueprintjs/icons/lib/css/blueprint-icons.css";
import "@blueprintjs/core/lib/css/blueprint.css";

import { DefaultItemListRenderer } from "./plugins/DefaultItemListRenderer";
import { DefaultItemRenderer } from "./plugins/DefaultItemRenderer";

ReactDOM.render(
  <React.StrictMode>
    <Router>
      <Switch>
        <Route path="/:id">
          {/* For more information see the 'Customization' section of the README.md file. */}
          <ItemView itemRenderer={DefaultItemRenderer} />
        </Route>
        <Route path="/">
          {/* For more information see the 'Customization' section of the README.md file. */}
          <AllItemView
            itemListRenderer={DefaultItemListRenderer}
            itemRenderer={DefaultItemRenderer}
            pagination={true}
            resultsPerPage={9}
          />
        </Route>
      </Switch>
    </Router>
  </React.StrictMode>,
  document.getElementById("root")
);
