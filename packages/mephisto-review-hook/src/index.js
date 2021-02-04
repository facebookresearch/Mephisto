import React, { useState, useEffect } from "react";

function useMephistoReview({ useMock, mock } = {}) {
  const [data, setData] = useState(null);
  const [counter, setCounter] = useState(0);
  const [error, setError] = useState(null);

  const isMock =
    mock !== undefined && (useMock === undefined || useMock === true);

  useEffect(() => {
    if (isMock) {
      return;
    }

    fetch("/data_for_current_task")
      .catch((err) => {
        setError({ type: "DATA_RETRIEVAL", error: err });
      })
      .then((res) => res.json())
      .then((data) => setData(data))
      .catch((err) => {
        setError({ type: "DATA_PARSE", error: err });
      });
  }, [counter]);

  const submitData = React.useCallback(
    (data) => {
      fetch("/submit_current_task", {
        method: "POST",
        body: JSON.stringify(data),
      })
        .catch((err) => {
          setError({ type: "RESPONSE_SUBMIT", error: err });
        })
        .then(() => setCounter(counter + 1));
    },
    [counter, setCounter]
  );

  if (isMock) {
    return mock;
  }

  return {
    isLoading: !data,
    data: data && data.data,
    isFinished: data && data.finished,
    submit: submitData,
    error: error,
  };
}

export { useMephistoReview };
