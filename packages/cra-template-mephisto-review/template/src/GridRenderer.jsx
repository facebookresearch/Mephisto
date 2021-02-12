import React, { useState } from "react";
import { Redirect } from "react-router-dom";
import { useMephistoReview } from "mephisto-review-hook";
import { H4, H3, H2, H1, InputGroup, Button } from "@blueprintjs/core";
import { Tooltip2 } from "@blueprintjs/popover2";
import GridView from "./GridView";
import Pagination from "./components/Pagination";
import "./GridRenderer.css";

function GridRenderer() {
  const resultsPerPage = 9;
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState("");
  const [filtersBuffer, setFiltersBuffer] = useState("");
  const [filterTimeout, setFilterTimeout] = useState(null);

  const {
    data,
    isFinished,
    isLoading,
    error,
    mode,
    totalPages,
  } = useMephistoReview({ page, resultsPerPage, filters });

  const delaySetFilters = (filtersStr) => {
    setFiltersBuffer(filtersStr);
    if (filterTimeout) {
      clearTimeout(filterTimeout);
    }
    setFilterTimeout(
      setTimeout(() => {
        setFilters(filtersStr);
      }, 3000)
    );
  };

  const setFiltersImmediately = () => {
    if (filterTimeout) {
      clearTimeout(filterTimeout);
    }
    setFilters(filtersBuffer);
  };

  const searchButton = (
    <Button round={true} onClick={setFiltersImmediately}>
      Search
    </Button>
  );

  if (mode === "OBO") return <Redirect to={`/${data && data.id}`} />;
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
            {data && data.length > 0 && (
              <H3>Please click on the following data cards to review them:</H3>
            )}
          </div>
          <Tooltip2
            className="search-box"
            content="Separate multiple filters with commas"
          >
            <InputGroup
              leftIcon="search"
              large={true}
              round={true}
              onChange={(event) => delaySetFilters(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") setFiltersImmediately();
              }}
              placeholder="Filter data..."
              value={filtersBuffer}
              rightElement={searchButton}
            />
          </Tooltip2>
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
            <div className="grid-renderer-no-data">
              <H4>
                Sorry, no data available. Please provide Mephisto Review with
                some data by running mephisto review with either standard input
                of a CSV or JSON file or by using the "--db" flag along with the
                name of a task in mephistoDB as an argument. The task must have
                valid review data.
              </H4>
            </div>
          )}
        </>
      )}
    </main>
  );
}

export default GridRenderer;
