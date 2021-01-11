import React, { useState, useEffect } from "react";
import { useMephistoReview } from "mephisto-review-hook";
import "./App.css";

function App() {
  const { data, isFinished, isLoading, submit, error } = useMephistoReview();

  return (
    <div className="App">
      {error && <div>{JSON.stringify(error)}</div>}
      {isLoading ? (
        <h1>Loading...</h1>
      ) : isFinished ? (
        <h1>Done reviewing!</h1>
      ) : (
        <header className="App-header">
          <pre>{JSON.stringify(data, 2)}</pre>
          <button onClick={() => submit({ result: "approved" })}>
            Approve
          </button>
          <button onClick={() => submit({ result: "rejected" })}>Reject</button>
        </header>
      )}
    </div>
  );
}

export default App;
