import React, { Component } from "react";
import "./App.css";
import { BrowserRouter as Router, Route, Switch, Link } from "react-router-dom";
import Dashboard from "./Dashboard";
import Review from "./Review";
import TaskGallery from "./TaskGallery";
import Splash from "./Splash";
import { ReactComponent as M } from "./M.svg";

class App extends Component {
  render() {
    return (
      <div className="App">
        <Router>
          <header className="App-header">
            <Switch>
              <Route
                exact
                path="/"
                render={() => (
                  <Link to="/dashboard">
                    {/* <img
                      alt="logo"
                      className="logo"
                      src="https://parl.ai/static/img/icon.png"
                      style={{
                        width: 60
                      }}
                    /> */}
                    <M />
                    mephisto
                  </Link>
                )}
              />
              <Route
                render={() => (
                  <Link to="/dashboard">
                    {/* <img
                      alt="logo"
                      className="logo"
                      src="https://parl.ai/static/img/icon.png"
                      style={{
                        width: 60
                      }}
                    /> */}
                    <M />
                    mephisto
                  </Link>
                )}
              />
            </Switch>
          </header>

          <Route exact path="/" render={() => <Dashboard />} />
          <Route exact path="/dashboard" render={() => <Dashboard />} />
          <Route exact path="/task-gallery" render={() => <TaskGallery />} />
          <Route exact path="/review" render={() => <Review />} />
        </Router>
      </div>
    );
  }
}

export default App;
