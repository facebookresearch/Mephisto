import React from "react";
import { useMephistoReview } from "mephisto-review-hook";
import { useParams, useHistory, Link } from "react-router-dom";
import {
  Button,
  Navbar,
  NavbarGroup,
  NavbarDivider,
  NavbarHeading,
  Alignment,
  Position,
  Toaster,
} from "@blueprintjs/core";
import { DefaultItemRenderer } from "../plugins/DefaultItemRenderer";

const AppToaster = Toaster.create({
  className: "recipe-toaster",
  position: Position.TOP,
});

function ItemView({ itemRenderer: ItemRenderer = DefaultItemRenderer }) {
  const { id } = useParams();
  const {
    data: item,
    isFinished,
    isLoading,
    submit,
    error,
    mode,
  } = useMephistoReview({ taskId: id });

  const history = useHistory();

  const confirmReview = () => {
    if (mode === "OBO") {
      history.push("/");
    } else {
      AppToaster.show({ message: "Review Sent!" });
    }
  };

  const reviewError = (error) => {
    AppToaster.show({ message: `ERROR: ${error}` });
  };

  const buttonDisable = error || isFinished || isLoading || item == null;

  return (
    <>
      <Navbar fixedToTop={true}>
        <div className="navbar-wrapper">
          <NavbarGroup>
            {mode === "ALL" ? (
              <>
                <Link to="/" style={{ textDecoration: "none" }}>
                  <Button intent="primary" icon="caret-left" id="home-button">
                    <b>Mephisto Review</b>
                  </Button>
                </Link>
                <NavbarDivider />
              </>
            ) : null}
            <NavbarHeading className="navbar-header">
              <b>Please review the following item:</b>
            </NavbarHeading>
          </NavbarGroup>
          <NavbarGroup align={Alignment.RIGHT}>
            <Button
              className="btn"
              intent="danger"
              disabled={buttonDisable}
              id="reject-button"
              onClick={async () => {
                var response = await submit({ result: "rejected" });
                if (response == "SUCCESS") {
                  confirmReview();
                } else if (response) {
                  reviewError(response);
                }
              }}
            >
              <b>REJECT</b>
            </Button>
            <Button
              className="btn"
              intent="success"
              disabled={buttonDisable}
              id="approve-button"
              onClick={async () => {
                var response = await submit({ result: "approved" });
                if (response == "SUCCESS") {
                  confirmReview();
                } else if (response) {
                  reviewError(response);
                }
              }}
            >
              <b>APPROVE</b>
            </Button>
          </NavbarGroup>
        </div>
      </Navbar>
      <main className="item-view">
        {error && (
          <h5 className="error item-view-error">
            Error: {JSON.stringify(error)}
          </h5>
        )}
        {isLoading ? (
          <h1 className="item-view-message">Loading...</h1>
        ) : isFinished ? (
          <h1 className="item-view-message">
            Done reviewing! You can close this app now
          </h1>
        ) : item ? (
          <ItemRenderer item={item} />
        ) : (
          <div className="item-view-message item-view-no-data">
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

export default ItemView;
