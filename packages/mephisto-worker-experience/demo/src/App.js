import React from "react";
import "./index.css";
import { Tips } from "mephisto-worker-experience";

function App() {
  return (
    <div className="card">
      <h1>Here Are Some Tips:</h1>
      <Tips
        handleSubmit={(tipData) => console.log(tipData)}
        list={[
          {
            header: "Functional or Class Components?",
            text:
              "It is generally advised to use functional components as they are thought to be the future of React.",
          },
          {
            header: "When to Use Context?",
            text:
              "To avoid having to pass props down 3+ levels, the createContext() and useContext() methods can be used.",
          },
        ]}
      />
    </div>
  );
}

export default App;
