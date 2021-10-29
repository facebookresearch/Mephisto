import React from "react";
import { Link } from "react-router-dom";
import { DefaultItemRenderer } from "../DefaultItemRenderer";
import "./DefaultCollectionRenderer.css";

function DefaultCollectionRenderer({
  data,
  itemRenderer: ItemRenderer = DefaultItemRenderer,
}) {
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

export { DefaultCollectionRenderer };
