import React from "react";
import { Link } from "react-router-dom";
import { JSONItem } from "../JSONItem";
import "./GridCollection.css";

function GridCollection({ data, itemRenderer: ItemRenderer = JSONItem }) {
  return data && data.length > 0 ? (
    <div className="default-collection-renderer-container">
      {data.map((item) => {
        return (
          <Link
            to={`/${item.id}`}
            style={{ textDecoration: "none" }}
            key={item.id}
            id={`item-${item.id}`}
          >
            <ItemRenderer item={item} />
          </Link>
        );
      })}
    </div>
  ) : null;
}

export { GridCollection };
