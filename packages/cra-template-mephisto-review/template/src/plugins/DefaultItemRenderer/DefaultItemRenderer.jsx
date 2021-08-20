import React, { useRef, useEffect, useState } from "react";
import { H6, Card, Elevation } from "@blueprintjs/core";
import "./DefaultItemRenderer.css";

function DefaultItemRenderer({ item }) {
  const SMALL_CARD_WIDTH_LIMIT = 1000;
  const [cardWidth, setCardWidth] = useState(0);
  const card = useRef();

  useEffect(() => {
    setCardWidth(card.current.offsetWidth);
  }, []);

  const smallCard = cardWidth < SMALL_CARD_WIDTH_LIMIT;

  return (
    <div
      ref={card}
      className="default-item-renderer"
      id={`item-view-${item && item.id}`}
    >
      <Card elevation={Elevation.TWO} interactive={smallCard}>
        <pre
          className={
            smallCard
              ? "default-item-renderer-pre small"
              : "default-item-renderer-pre"
          }
        >
          {JSON.stringify(item && item.data)}
        </pre>
        <H6>
          <b>ID: {item && item.id}</b>
        </H6>
      </Card>
    </div>
  );
}

export default DefaultItemRenderer;
