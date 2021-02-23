import React from "react";
import ReactDOM from "react-dom";
import "./css/Index.css";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
import AllItemView from "./AllItemView";
import ItemView from "./ItemView";
import GridView from "./components/GridView";
import DefaultItemRenderer from "./components/DefaultItemRenderer";
import "normalize.css/normalize.css";
import "@blueprintjs/icons/lib/css/blueprint-icons.css";
import "@blueprintjs/core/lib/css/blueprint.css";
import "@blueprintjs/popover2/lib/css/blueprint-popover2.css";

ReactDOM.render(
  <React.StrictMode>
    <Router>
      <Switch>
        <Route path="/:id">
          {/*
          This route allows users to review data for individual items.
          Add custom renderers for item data by adding an 'itemRenderer' property.
          For more information see the 'Customization' section of the README.md file.
          */}
          <ItemView itemRenderer={DefaultItemRenderer} />
        </Route>
        <Route path="/">
          {/*
          This route shows all data items being reviewed by page.
          If you do not wish to use pagination, set the 'pagination' property to 'false' (default is true).
          The default number of results per page is 9, however can be adjusted by setting the 'resultsPerPage' property (must be an integer).
          Add custom renderers for the layout of all items by passing an 'itemListRenderer' property.
          Add custom itemRenderers for individual items by adding an 'itemRenderer' property.
          For more information see the 'Customization' section of the README.md file.
          */}
          <AllItemView
            itemListRenderer={GridView}
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
