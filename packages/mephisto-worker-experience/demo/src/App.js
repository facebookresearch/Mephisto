import React from "react";
import "./index.css";
import { Tips, createTip } from "mephisto-worker-experience";

function App() {
  return (
    <div className="container">
      <Tips
        handleSubmit={(tipData) =>
          console.log(createTip(tipData.header, tipData.text))
        }
        maxHeight="25rem"
        maxWidth="25rem"
        placement="right-start"
        list={[
          {
            header: "Functional or Class Components?",
            text: "This is some tip text",
          },
          {
            header: "When to Use Context?",
            text: "This is some other tip text",
          },
        ]}
      />
    </div>
  );
}

export default App;
