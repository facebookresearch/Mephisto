/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import { useEffect } from "react";
import * as React from "react";
import "./ColumnTitleWithSort.css";

export enum SortArrowsState {
  ASC = "asc",
  DESC = "desc",
  INACTIVE = "inactive",
}

const NextStateMapping = {
  [SortArrowsState.INACTIVE]: SortArrowsState.ASC,
  [SortArrowsState.ASC]: SortArrowsState.DESC,
  [SortArrowsState.DESC]: SortArrowsState.INACTIVE,
};

type SortArrowsPropsType = {
  state: SortArrowsState;
};

function SortArrows(props: SortArrowsPropsType) {
  return (
    <div className={`sort-arrows ${props.state}`}>
      {props.state === SortArrowsState.INACTIVE && (
        <>
          <i className={`sort-arrows-up`}>&#x25b4;</i>
          <i className={`sort-arrows-down`}>&#x25be;</i>
        </>
      )}

      {props.state === SortArrowsState.ASC && (
        <i className={`sort-arrows-up`}>&#x25B2;</i>
      )}

      {props.state === SortArrowsState.DESC && (
        <i className={`sort-arrows-down`}>&#x25BC;</i>
      )}
    </div>
  );
}

type ColumnTitleWithSortPropsType = {
  onClick?: Function;
  state?: SortArrowsState;
  title: string | React.ReactElement;
};

function ColumnTitleWithSort(props: ColumnTitleWithSortPropsType) {
  const [state, setState] = React.useState<SortArrowsState>(
    props.state || SortArrowsState.INACTIVE
  );

  // Methods

  function onClick() {
    let newState = NextStateMapping[state];
    props.onClick && props.onClick(newState);
    setState(newState);
  }

  // Effects

  useEffect(() => {
    if (props.state !== state) {
      setState(props.state);
    }
  }, [props.state]);

  return (
    <div className={`column-title-with-sort`} onClick={onClick}>
      {props.title}

      <SortArrows state={state} />
    </div>
  );
}

export default ColumnTitleWithSort;
