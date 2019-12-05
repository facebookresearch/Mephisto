import React from "react";
import "./splash.css";
import { Link } from "react-router-dom";

export default () => {
  return (
    <div className="hero">
      A model is only as good
      <br />
      as the data it's trained with.
      <div style={{ marginTop: 30, marginBottom: -30 }}>
        <Link to="/dashboard" className="btn rounded">
          Get Started
        </Link>
      </div>
      <div style={{ transform: "perspective(600px) rotateX(30deg)" }}>
        <img src="/screenshot.png" width="70%" />
      </div>
    </div>
  );
};
