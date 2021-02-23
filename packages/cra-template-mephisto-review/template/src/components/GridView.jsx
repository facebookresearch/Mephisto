import React from "react";
import { Link } from "react-router-dom";
import { Card, Elevation } from "@blueprintjs/core";
import DefaultItemRenderer from "./DefaultItemRenderer";
import "./css/GridView.css";

function GridView({ data, itemRenderer: ItemRenderer = DefaultItemRenderer }) {
  return data && data.length > 0 ? (
    <div className="grid-container">
      {data.map((item) => {
        return (
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
              <div className="grid-item-content">
                <ItemRenderer item={item} />
              </div>
            </Card>
          </Link>
        );
      })}
    </div>
  ) : null;
}

export default GridView;
