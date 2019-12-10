import React, { Component } from "react";
import "./App.css";
import { BrowserRouter as Router, Route, Switch, Link } from "react-router-dom";
import Dashboard from "./Dashboard";
import Review from "./Review";
import TaskGallery from "./TaskGallery";
import { ReactComponent as M } from "./M.svg";
import useAxios from "axios-hooks";

function App() {
  const [{ data, loading, error }, refetch] = useAxios({
    url: "requesters",
    baseURL: "http://localhost:5000/api/v1/"
  });

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

          {!loading && (
            <div>
              {/* {JSON.stringify(data)} */}
              <select>
                {data.requesters.map(r => (
                  <option>
                    {r.requester_name} - {r.provider_type}
                  </option>
                ))}
              </select>
            </div>
          )}
        </header>

        <Route exact path="/" render={() => <Dashboard />} />
        <Route exact path="/dashboard" render={() => <Dashboard />} />
        <Route exact path="/task-gallery" render={() => <TaskGallery />} />
        <Route exact path="/review" render={() => <Review />} />
      </Router>
    </div>
  );
}

export default App;
