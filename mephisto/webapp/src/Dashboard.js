import React from "react";
import { Link } from "react-router-dom";
import useAxios from "axios-hooks";

export default () => {
  return (
    <div className="page-body">
      <div className="card-outer-container">
        <div className="card-container">
          <div className="card create-task">
            <h3>
              <span className="badge">1</span>
              <em>Create</em> a task
            </h3>
            {/* <p>
Edit <code>src/App.js</code> and save to reload.
</p> */}
            <div>
              <p>
                You will need an MTurk Requester Account and an AWS account
                (separate accounts).
                <a
                  className="App-link"
                  href="https://parl.ai/docs/tutorial_mturk.html#running-a-task"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Setting up AWS »
                </a>
              </p>
              <p>
                We have a growing collection of tasks already available. You can
                re-use one of them, clone &amp; modify one of them to create a
                similar yet different task, or create a completely new custom
                task altogether. Custom tasks can range from simple static
                pages, to multi-agent dialogue, to dynamic &amp; interactive
                React applications!
                <Link className="App-link" to="/task-gallery">
                  View gallery of existing tasks »
                </Link>
                <a
                  className="App-link"
                  href="https://parl.ai/docs/tutorial_task.html#creating-a-new-task-the-more-complete-way"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Create a custom task »
                </a>
              </p>
            </div>
          </div>
          <div className="card">
            <h3>
              <span className="badge">2</span>
              <em>Launch</em> tasks
            </h3>
            <p>
              You currently have <strong>3 tasks</strong> running live.
            </p>
            {[1, 2, 3].map(i => (
              <div className="live-task interactive">
                <div className="title">
                  {i > 1 ? "semantic annotation" : "LIGHT pilot (v2)"}
                  {i === 1 && <span className="sandbox">Sandbox</span>}
                </div>
                <div className="hyperparameters">
                  {
                    [null].map(() => {
                      return Object.entries({
                        dataset: "twitter",
                        model: "v3.123",
                        enableSafety: true,
                        saveDataFile: "localDB"
                      }).map(([key, value]) => (
                        <span className="hyperparameter">
                          <span className="key">{key}</span>=
                          <span className="value">{value.toString()}</span>
                        </span>
                      ));
                    })[0]
                  }
                </div>
                <div className="details">
                  Started 8 hours ago. 25 completed HITs. 3 disconnects.
                </div>
              </div>
            ))}
            <button className="btn">Launch a new task</button>
          </div>
          <div className="card">
            <h3>
              <span className="badge">3</span>
              <em>Review</em> data
            </h3>
            {/* <p>
Edit <code>src/App.js</code> and save to reload.
</p> */}
            {/* {[{amount: 12, daysPending: 1}]} */}
            <p>
              You have{" "}
              <Link to="/review" alt="link">
                300 HITs
              </Link>{" "}
              left to review.
            </p>
            {/* <p class="warning">
  <a href="#" alt="link">
    10 tasks
  </a>{" "}
  will be auto-reviewed by tomorrow.
</p> */}

            <Link className="unstyled" to="/review">
              <div className="live-task interactive">
                <div className="title">LIGHT dialogue</div>
                <div className="hyperparameters">
                  {
                    [null].map(() => {
                      return Object.entries({
                        dataset: "twitter",
                        model: "v3.123",
                        enableSafety: true,
                        saveDataFile: "localDB"
                      }).map(([key, value]) => (
                        <span className="hyperparameter">
                          <span className="key">{key}</span>=
                          <span className="value">{value.toString()}</span>
                        </span>
                      ));
                    })[0]
                  }
                </div>
                <div className="details">
                  <div className="metrics highlight-first">
                    <div className="metric">
                      70<label>Unreviewed</label>
                    </div>
                    <div className="metric">
                      300<label>Approved</label>
                    </div>
                    <div className="metric">
                      23<label>Rejected</label>
                    </div>
                  </div>
                  {/* Reviewed: 300 | Unreviewed: <strong>80</strong> */}
                  <p className="warning">
                    Warning: 10 HITs are nearing their 2 week deadline and risk
                    being auto-approved.
                  </p>
                </div>
              </div>
            </Link>
            <div className="live-task interactive">
              <div className="title">LIGHT dialogue (pilot v1)</div>
              <div className="hyperparameters">
                {
                  [null].map(() => {
                    return Object.entries({
                      dataset: "twitter",
                      model: "v3.123",
                      enableSafety: true,
                      saveDataFile: "localDB"
                    }).map(([key, value]) => (
                      <span className="hyperparameter">
                        <span className="key">{key}</span>=
                        <span className="value">{value.toString()}</span>
                      </span>
                    ));
                  })[0]
                }
              </div>
              <div className="details">
                <div className="metrics highlight-first">
                  <div className="metric">
                    230<label>Unreviewed</label>
                  </div>
                  <div className="metric">
                    300<label>Approved</label>
                  </div>
                  <div className="metric">
                    23<label>Rejected</label>
                  </div>
                </div>
              </div>
            </div>
            <div style={{ marginTop: 20 }}>
              <a
                className="App-link"
                href="#"
                target="_blank"
                rel="noopener noreferrer"
              >
                View all completed tasks »
              </a>
            </div>
            {/* <div className="bar" style={{ width: "50%" }}>
  &nbsp;
</div>
<div className="bar" style={{ width: "100%" }}>
  &nbsp;
</div> */}
          </div>
          <div className="card export-data">
            <h3>
              <span className="badge">4</span>
              <em>Export</em> data
            </h3>
            <p>
              Output data for tasks is stored in:{" "}
              <code>/data/&lt;task-name&gt;/&lt;run-id&gt;</code>
            </p>
            <p>
              Best practices:
              <ul>
                <li>
                  Use a Jupyter notebook to post-process your data to encode
                  reproducibility steps.
                </li>
              </ul>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
