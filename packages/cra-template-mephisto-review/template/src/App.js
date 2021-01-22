import React, { useState, useEffect } from "react";
import { useMephistoReview } from "mephisto-review-hook";
import "./App.css";

function App() {
  const { data, isFinished, isLoading, submit, error } = useMephistoReview();

  return (
    <div className="App">
      <header className="App-header">
        {error && <div>Error: {JSON.stringify(error)}</div>}
        {isLoading ? (
          <h1>Loading...</h1>
        ) : isFinished ? (
          <h1>Done reviewing! You can close this app now</h1>
        ) : (
          <>
            <p>Please review the following data:</p>
            <pre>{JSON.stringify(data, 2)}</pre>
            <div className="button-container">
              <button
                className="btn btn-green"
                onClick={() => submit({ result: "approved" })}
              >
                Approve
              </button>
              <button
                className="btn btn-red"
                onClick={() => submit({ result: "rejected" })}
              >
                Reject
              </button>
            </div>
          </>
        )}
      </header>
    </div>
  );
}

export default App;
