import React, { useState, useEffect, useCallback } from "react";
import { useMephistoReview as useMephistoReviewLegacy } from "./legacy";

function useMephistoReview({
  useMock,
  mock,
  taskId,
  page,
  resultsPerPage,
  filters,
  hostname = "",
} = {}) {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const isMock =
    mock !== undefined && (useMock === undefined || useMock === true);

  useEffect(() => {
    if (isMock) {
      return;
    }
    const DATA_URL = taskId
      ? `${hostname}/data/${taskId}`
      : `${hostname}/data?${page ? "page=" + page : ""}${
          resultsPerPage ? "&results_per_page=" + resultsPerPage : ""
        }${filters ? "&filters=" + encodeURIComponent(filters) : ""}`;
    setIsLoading(true);
    fetch(DATA_URL, { method: "GET" })
      .catch((err) => setError({ type: "DATA_RETRIEVAL", error: err }))
      .then((res) => res.json())
      .then((data) => setData(data))
      .catch((err) => setError({ type: "DATA_PARSE", error: err }))
      .then(() => setIsLoading(false));
  }, [taskId, page, resultsPerPage, filters]);

  const submitData = useCallback(
    async (data) => {
      var response = null;
      setIsLoading(true);
      await fetch(`${hostname}/data/${taskId}`, {
        method: "POST",
        body: JSON.stringify(data),
      })
        .catch((err) => setError({ type: "RESPONSE_SUBMIT", error: err }))
        .then((res) => res.json())
        .then((data) => (response = data && (data.result || data.error)))
        .catch((err) => setError({ type: "DATA_PARSE", error: err }))
        .then(() => setIsLoading(false));
      return response;
    },
    [taskId]
  );

  if (isMock) {
    return mock;
  }

  return {
    isLoading: isLoading,
    mode: data && data.mode,
    data: data && data.data,
    isFinished: data && data.finished,
    totalPages: (data && data.total_pages) || 1,
    submit: submitData,
    error: error,
  };
}

export { useMephistoReview, useMephistoReviewLegacy };
