import React from "react";
import { Link } from "react-router-dom";
import { Card, Divider, H4 } from "@blueprintjs/core";
import DefaultItemRenderer from "../components/DefaultItemRenderer";
import "./css/ListView.css";

/*
  EXAMPLE PLUGIN ALL DATA RENDERER
  Displays all mephisto review data as a list
*/
function ListView({ data, itemRenderer: Renderer = DefaultItemRenderer }) {
  return data && data.length > 0 ? (
    <Card className="list-container">
      {data.map((item, index) => (
        <>
          {index != 0 ? <Divider /> : null}
          <Link
            to={`/${item.id}`}
            style={{ textDecoration: "none" }}
            key={item.id}
          >
            <div className={index != 0 ? "list-item divider" : "list-item"}>
              <Renderer item={item} />
            </div>
          </Link>
        </>
      ))}
    </Card>
  ) : null;
}

export default ListView;
