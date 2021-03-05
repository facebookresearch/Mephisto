import React, { useState } from "react";
import { Redirect } from "react-router-dom";
import { useMephistoReview } from "mephisto-review-hook";
import {
  InputGroup,
  Button,
  Navbar,
  NavbarGroup,
  NavbarDivider,
  NavbarHeading,
  Alignment,
} from "@blueprintjs/core";
import { Tooltip2 } from "@blueprintjs/popover2";
import DefaultItemRenderer from "./plugins/DefaultItemRenderer";
import DefaultItemListRenderer from "./plugins/DefaultItemListRenderer";
import Pagination from "./components/Pagination";
import "./css/AllItemView.css";

function AllItemView({
  itemRenderer = DefaultItemRenderer,
  itemListRenderer: ItemListRenderer = DefaultItemListRenderer,
  pagination = true,
  resultsPerPage = 9,
}) {
  const [page, setPage] = useState(pagination ? 1 : null);
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
    <>
      <Navbar fixedToTop={true}>
        <div style={{ margin: "0 auto", width: "75vw" }}>
          <NavbarGroup>
            <NavbarHeading>
              <b>Mephisto Review</b>
            </NavbarHeading>
            <NavbarDivider />
          </NavbarGroup>
          <NavbarGroup align={Alignment.RIGHT}>
            <Tooltip2 content="Separate multiple filters with commas">
              <InputGroup
                style={{ width: "60vw" }}
                leftIcon="search"
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
          </NavbarGroup>
        </div>
      </Navbar>
      <main className="all-item-view">
        {error && (
          <h5 className="all-item-view-error error">
            Error: {JSON.stringify(error)}
          </h5>
        )}
        {isLoading ? (
          <h1 className="all-item-view-message">Loading...</h1>
        ) : isFinished ? (
          <h1 className="all-item-view-message">
            Done reviewing! You can close this app now
          </h1>
        ) : data && data.length > 0 ? (
          <>
            <ItemListRenderer data={data} itemRenderer={itemRenderer} />
            {pagination && totalPages > 1 ? (
              <Pagination
                totalPages={totalPages}
                page={page}
                setPage={setPage}
              />
            ) : null}
          </>
        ) : (
          <div className="all-item-view-message all-item-view-no-data">
            <h3>
              No data available. Please provide Mephisto Review with some data
              by running mephisto review with either standard input of a CSV or
              JSON file or by using the "--db" flag along with the name of a
              task in mephistoDB as an argument. The task must have valid review
              data.
            </h3>
          </div>
        )}
      </main>
    </>
  );
}

export default AllItemView;
