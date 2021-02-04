import React from "react";
import { useHistory } from "react-router-dom";
import { Card, Elevation, H4 } from "@blueprintjs/core";

function GridView({ data }) {
  const history = useHistory();

  return data && data.length > 0 ? (
    <div className="grid-container">
      {data.map((item) => (
        <Card
          key={item.id}
          interactive={true}
          elevation={Elevation.TWO}
          className="grid-item"
          onClick={() => history.push(`/${item.id}`)}
        >
          <div className="grid-item-text">
            <pre>{item.data}</pre>
          </div>
          <H4>
            <b>ID: {item.id}</b>
          </H4>
        </Card>
      ))}
    </div>
  ) : null;
}

export default GridView;
