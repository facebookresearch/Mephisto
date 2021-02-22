import React from "react";
import { H4 } from "@blueprintjs/core";

function DefaultItemRenderer({ item }) {
  return (
    <>
      <pre>{JSON.stringify(item.data)}</pre>
      <H4>
        <b>ID: {item.id}</b>
      </H4>
    </>
  );
}

export default DefaultItemRenderer;
