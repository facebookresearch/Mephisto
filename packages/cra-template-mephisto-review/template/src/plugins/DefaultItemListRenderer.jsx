import React from "react";
import { Link } from "react-router-dom";
import { Card, Elevation } from "@blueprintjs/core";
import DefaultItemRenderer from "./DefaultItemRenderer";
import "./css/DefaultItemListRenderer.css";

function DefaultItemListRenderer({
  data,
  itemRenderer: ItemRenderer = DefaultItemRenderer,
}) {
  return data && data.length > 0 ? (
    <div className="default-item-list-renderer-container">
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
              className="default-item-list-renderer-card"
            >
              <ItemRenderer item={item} />
            </Card>
          </Link>
        );
      })}
    </div>
  ) : null;
}

export default DefaultItemListRenderer;
