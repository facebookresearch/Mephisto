import React from "react";
import { Link } from "react-router-dom";
import "./review.css";
import samplePic from "./sample.png"

export default () => (
  <div
    style={{
      display: "flex",
      flexDirection: "row",
      maxWidth: 1440,
      width: "100%",
      margin: "0 auto",
      alignItems: "flex-start"
    }}
  >
    <div className="card">
      <h3>
        <span className="badge">3</span>
        <em>Review</em> data
      </h3>
      <p>
        You have{" "}
        <Link to="/review" alt="link">
          300 total HITs
        </Link>{" "}
        left to review across 5 tasks.
      </p>
      <div
        style={{
          background: "#ee1054",
          margin: "0px -20px",
          padding: "5px 20px",
          color: "white",
          fontWeight: "bold"
        }}
      >
        Currently Reviewing Task:
      </div>
      <div className="live-task">
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

          {/* <p className="warning">
            Warning: 10 HITs are nearing their 2 week deadline and risk being
            auto-approved.
          </p> */}
        </div>
      </div>
      <div
        style={{
          background: "#ee1054",
          margin: "0px -20px",
          padding: "5px 20px",
          color: "white",
          fontWeight: "bold"
        }}
      >
        Currently Reviewing User:
      </div>

      <div className="user_info">
        <div className="title">User #182</div>
        <div className="hyperparameters">
          {
            [null].map(() => {
              return Object.entries({
                "All-Time Approved": "96%",
                "All-Time Evaluated": "83",
                timezone: "EST",
                browser: "Chrome"
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
              3/3<label>Golden tasks</label>
            </div>
            <div className="metric">
              31<label>Submitted</label>
            </div>
            <div className="metric">
              0<label>Disconnects</label>
            </div>
          </div>
          <div
            className="metrics highlight-first anticipate-double"
            style={{ marginTop: 15 }}
          >
            <div className="metric">
              &mdash; / 0{" "}
              <label>
                Current Task: %&nbsp;Approved&nbsp;/&nbsp;#&nbsp;Evaluated
              </label>
            </div>
            {/* <div className="metric">
              96% / 3,000{" "}
              <label>
                All Tasks: %&nbsp;Approved&nbsp;/&nbsp;#&nbsp;Evaluated
              </label>
            </div> */}
          </div>
        </div>
      </div>
      <div
        style={{
          backgroundColor: "#ffffcf",
          padding: "5px 10px 10px",
          border: "1px solid #f5f5e0"
        }}
      >
        <button className="btn" style={{ background: "green" }}>
          Approve
        </button>
        <button className="btn">Approve all by this user</button>
        <button className="btn" style={{ background: "crimson" }}>
          Reject
        </button>
      </div>
    </div>
    <div
      className="card"
      style={{
        flex: "1",
        backgroundColor: "white",
        width: "100%",
        maxWidth: "none",
        margin: "15px 20px 0 10px",
        minHeight: 300
      }}
    >
      <div className="review-control-panel">&nbsp;</div>
      <div
        className="task-frame"
        style={{
          backgroundColor: "white",
          color: "black"
          //   border: "3px solid #ddd"
        }}
      >
        <img src={samplePic} width="100%" />
      </div>
    </div>
  </div>
);
