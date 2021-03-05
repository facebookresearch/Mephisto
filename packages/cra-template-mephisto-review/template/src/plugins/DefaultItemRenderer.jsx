import React from "react";
import { H6 } from "@blueprintjs/core";
import "./css/DefaultItemRenderer.css";

function DefaultItemRenderer({ item }) {
  return (
    <div className="default-item-renderer">
      <pre>{JSON.stringify(item && item.data)}</pre>
      <H6>
        <b>ID: {item && item.id}</b>
      </H6>
    </div>
  );
}

export default DefaultItemRenderer;
