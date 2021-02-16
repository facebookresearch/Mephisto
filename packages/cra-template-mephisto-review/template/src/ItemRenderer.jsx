import React from "react";
import { useMephistoReview } from "mephisto-review-hook";
import { useParams, useHistory, Link } from "react-router-dom";
import { Button, H2, Card, Elevation } from "@blueprintjs/core";
import AppToaster from "./components/AppToaster";
import "./ItemRenderer.css";

function App() {
  const { id } = useParams();
  const {
    data,
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

  return (
    <main className="Item-Renderer">
      {mode === "ALL" ? (
        <Link to="/" style={{ textDecoration: "none" }}>
          <Button
            intent="primary"
            large={true}
            icon="caret-left"
            className="home-button"
          >
            <b>BACK</b>
          </Button>
        </Link>
      ) : null}
      {error && <h5 className="error">Error: {JSON.stringify(error)}</h5>}
      {isLoading ? (
        <h1>Loading...</h1>
      ) : isFinished ? (
        <h1>Done reviewing! You can close this app now</h1>
      ) : (
        <>
          <H2>Please review the following data:</H2>
          <Card className="item" elevation={Elevation.TWO}>
            <pre>{JSON.stringify(data && data.data)}</pre>
          </Card>
          <div className="button-container">
            <Button
              className="btn"
              intent="danger"
              large={true}
              disabled={data == null}
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
              large={true}
              disabled={data == null}
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
          </div>
        </>
      )}
    </main>
  );
}

export default App;
