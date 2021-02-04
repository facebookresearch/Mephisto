import React from "react";
import { Button, Icon, Intent } from "@blueprintjs/core";
import "./components.css";

function Pagination({ page = 1, totalPages = 1, setPage = () => {} }) {
  const MAX_CELLS = 7;
  const CELL_MID_LEN = ~~(MAX_CELLS / 2);

  let pages = [];

  if (totalPages > MAX_CELLS) {
    pages[0] = { number: 1 };
    pages[1] = { number: 2 };
    pages[MAX_CELLS - 2] = { number: totalPages - 1 };
    pages[MAX_CELLS - 1] = { number: totalPages };

    if (page <= CELL_MID_LEN) {
      pages[MAX_CELLS - 2].ellipsis = true;
      for (let i = 2; i < MAX_CELLS - 2; i++) {
        pages[i] = { number: i + 1 };
      }
    } else if (totalPages - page < CELL_MID_LEN) {
      pages[1].ellipsis = true;
      for (let i = 2; i < MAX_CELLS - 2; i++) {
        pages[i] = { number: totalPages - MAX_CELLS + i + 1 };
      }
    } else {
      pages[1].ellipsis = true;
      pages[MAX_CELLS - 2].ellipsis = true;

      pages[CELL_MID_LEN] = { number: page };
      for (let i = 1; i < MAX_CELLS - 5; i++) {
        pages[CELL_MID_LEN + i] = { number: page + i };
        pages[CELL_MID_LEN - i] = { number: page - i };
      }
    }
  } else {
    for (let i = 0; i < totalPages; i++) {
      pages[i] = { number: i + 1, ellipsis: false };
    }
  }

  pages.forEach((p) => {
    if (p.number === page) p.active = true;
  });

  const leftArrow = page > 1;
  const rightArrow = page < totalPages;

  return (
    <div className="pt-button-group pagination">
      <Button
        large={true}
        iconName="chevron-left"
        disabled={!leftArrow}
        onClick={() => setPage(page - 1)}
      >
        <Icon icon="chevron-left" />
      </Button>
      {pages.map((p) => (
        <Button
          large={true}
          text={p.ellipsis ? "..." : p.number}
          key={p.number}
          disabled={p.ellipsis}
          intent={p.active ? Intent.PRIMARY : Intent.DEFAULT}
          onClick={() => setPage(p.number)}
        />
      ))}
      <Button
        large={true}
        disabled={!rightArrow}
        onClick={() => setPage(page + 1)}
      >
        <Icon icon="chevron-right" />
      </Button>
    </div>
  );
}

export default Pagination;
