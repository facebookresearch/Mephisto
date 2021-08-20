import React from "react";
import { Link } from "react-router-dom";
import { DefaultItemRenderer } from "../DefaultItemRenderer";
import "./DefaultItemListRenderer.css";

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
            id={`item-${item.id}`}
          >
            <ItemRenderer item={item} />
          </Link>
        );
      })}
    </div>
  ) : null;
}

export default DefaultItemListRenderer;
