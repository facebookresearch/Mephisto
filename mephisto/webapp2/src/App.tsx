import React from "react";
import "./App.css";
import PrepareWidget from "./widgets/Prepare";
import LaunchWidget from "./widgets/Launch";
import ReviewWidget from "./widgets/Review";

const App: React.FC = () => {
  return (
    <div className="App">
      <div className="above-the-fold"></div>
      <header>
        <h1 className="bp3-heading">mephisto</h1>
        <em
          className="bp3-italics bp3-text-large bp3-text-disabled"
          style={{ position: "relative", top: -8 }}
        >
          crowdsourcing without the hassle
        </em>
      </header>
      <div className="container">
        <PrepareWidget />
        <LaunchWidget />
        <ReviewWidget />
      </div>
    </div>
  );
};

export default App;
