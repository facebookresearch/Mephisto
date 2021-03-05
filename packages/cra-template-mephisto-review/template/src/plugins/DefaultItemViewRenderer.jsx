import React from "react";
import { H5, Card, Elevation } from "@blueprintjs/core";
import "./css/DefaultItemViewRenderer.css";

function DefaultItemViewRenderer({ item }) {
  return (
    <Card className="default-item-view-renderer" elevation={Elevation.TWO}>
      <pre>{JSON.stringify(item && item.data)}</pre>
      <H5>
        <b>ID: {item && item.id}</b>
      </H5>
    </Card>
  );
}

export default DefaultItemViewRenderer;
