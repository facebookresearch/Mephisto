import React from "react";
import { Link } from "react-router-dom";
import { Card, Elevation, H4 } from "@blueprintjs/core";
import DefaultItemRenderer from "./DefaultItemRenderer";
import "./css/gridView.css";

function GridView({ data, itemRenderer: Renderer }) {
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
                {Renderer ? (
                  <Renderer item={item} />
                ) : (
                  <DefaultItemRenderer item={item} />
                )}
              </div>
            </Card>
          </Link>
        );
      })}
    </div>
  ) : null;
}

export default GridView;
