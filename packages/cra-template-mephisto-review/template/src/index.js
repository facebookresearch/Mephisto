import React from "react";
import ReactDOM from "react-dom";
import "./css/index.css";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
import AllDataView from "./AllDataView";
import ItemView from "./ItemView";
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
          Add custom renderers for item data by adding a 'itemRenderer' property to ItemReview.
          The itemRenderer property must be a react component.
          The itemRenderer component will be passed down an property of 'item'
          The item property will contain the properties of 'data' representing the JSON data of the review item
            as well as an 'id' representing the 0 indexed position of the item in the review data
          */}
          <ItemView />
        </Route>
        <Route path="/">
          {/*
          This route shows all data items being reviewed by page

          If you do not wish to use pagination, set the 'pagination' property to 'false' (default is true)
          The default number of results per page is 9, however can be adjusted by setting the 'resultsPerPage' property (must be an integer)

          Add custom renderers for rendering all data by passing a 'renderer' property.
          The renderer property must be a react component.
          The renderer component will be passed down an property of 'data', which is an array of all data items.
          The renderer component will also be passed down an property of 'itemRenderer' which renderers the data of a single item.
          The itemRenderer can be placed in each of the individual item views in your renderer

          By default the item renderer will be a header with the item id and a pre containing the stringified JSON data from the item
          Optionally, the item renderer can be replaced by providing an 'itemRenderer' property to AllDataView
          The itemRenderer must be a react component.
          The itemRenderer will be passed down an property of 'item'
          The item property will contain the propertys of 'data' representing the JSON data of the review item
            as well as an 'id' representing the 0 indexed position of the item in the review data
          */}
          <AllDataView />
        </Route>
      </Switch>
    </Router>
  </React.StrictMode>,
  document.getElementById("root")
);
