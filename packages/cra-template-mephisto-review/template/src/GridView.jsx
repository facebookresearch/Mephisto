import React from "react";
import { Link } from "react-router-dom";
import { Card, Elevation, H4 } from "@blueprintjs/core";

function GridView({ data }) {
  return data && data.length > 0 ? (
    <div className="grid-container">
      {data.map((item) => (
        <Link
          to={`/${item.id}`}
          style={{ textDecoration: "none" }}
          key={item.id}
        >
          <Card
            interactive={true}
            elevation={Elevation.TWO}
            className="grid-item"
          >
            <div className="grid-item-text">
              <pre>{JSON.stringify(item.data)}</pre>
            </div>
            <H4>
              <b>ID: {item.id}</b>
            </H4>
          </Card>
        </Link>
      ))}
    </div>
  ) : null;
}

export default GridView;
