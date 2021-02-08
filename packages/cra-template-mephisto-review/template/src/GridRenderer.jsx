import React, { useState } from "react";
import { Redirect } from "react-router-dom";
import { useMephistoReview } from "mephisto-review-hook";
import { H5, H3, H2, H1 } from "@blueprintjs/core";
import GridView from "./GridView";
import Pagination from "./components/Pagination";
import "./GridRenderer.css";

function GridRenderer() {
  const resultsPerPage = 9;
  const [page, setPage] = useState(1);
  const {
    data,
    isFinished,
    isLoading,
    error,
    mode,
    taskId,
    totalPages,
  } = useMephistoReview({ page, resultsPerPage });

  if (mode === "OBO") return <Redirect to={`/${taskId}`} />;
  return (
    <main className="grid-renderer">
      {error && <h5 className="error">Error: {JSON.stringify(error)}</h5>}
      {isLoading ? (
        <H1>Loading...</H1>
      ) : isFinished ? (
        <H1>Done reviewing! You can close this app now</H1>
      ) : (
        <>
          <div className="grid-renderer-header">
            <H2>
              <b>Welcome to Mephisto Review</b>
            </H2>
            <H3>Please click on the following data cards to review them:</H3>
          </div>
          {data && data.length > 0 ? (
            <>
              <GridView data={data} />
              <Pagination
                totalPages={totalPages}
                page={page}
                setPage={setPage}
              />
            </>
          ) : (
            <H5 className="grid-renderer-header">
              Sorry, no data available. Please provide Mephisto Review with some
              data by running mephisto review with either standard input of a
              CSV or JSON file or by using the "--db" flag along with the name
              of a task in mephistoDB as an argument. The task must have valid
              review data.
            </H5>
          )}
        </>
      )}
    </main>
  );
}

export default GridRenderer;
