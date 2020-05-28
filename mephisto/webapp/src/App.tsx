/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import "./App.css";
import PrepareWidget from "./widgets/Prepare";
import LaunchWidget from "./widgets/Launch";
import ReviewWidget from "./widgets/Review";
import { BrowserRouter as Router, Switch, Route, Link } from "react-router-dom";
import { Card } from "@blueprintjs/core";
import GridReview from "./widgets/GridReview";

const App: React.FC = () => {
  return (
    <Router>
      <div className="App">
        <div className="above-the-fold"></div>
        <header>
          <div>
            <h1 className="bp3-heading">
              <Link to="/">mephisto</Link>
            </h1>
            <em
              className="bp3-italics bp3-text-large bp3-text-disabled"
              style={{ position: "relative", top: -8 }}
            >
              crowdsourcing without the tears
            </em>
          </div>
        </header>
        <div>
          <Switch>
            <Route exact path="/">
              <div className="container">
                <PrepareWidget />
                <LaunchWidget />
                <ReviewWidget />
              </div>
            </Route>
            <Route
              path="/review/:id"
              render={({ match: { params } }) => (
                <div style={{ margin: 30 }}>
                  <div className="bp3-card bp3-elevation-3 widget widget">
                    <GridReview id={params.id} />
                  </div>
                </div>
              )}
            />
          </Switch>
        </div>
      </div>
    </Router>
  );
};

export default App;
