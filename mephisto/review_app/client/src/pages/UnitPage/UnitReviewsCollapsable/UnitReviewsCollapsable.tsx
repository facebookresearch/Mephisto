/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import CollapsableBlock from "components/CollapsableBlock/CollapsableBlock";
import { DEFAULT_DATE_FORMAT } from "consts/format";
import { STATUS_COLOR_CLASS_MAPPING } from "consts/review";
import { capitalizeString } from "helpers";
import * as moment from "moment";
import * as React from "react";
import { Table } from "react-bootstrap";
import "./UnitReviewsCollapsable.css";

type UnitReviewsCollapsablePropsType = {
  className?: string;
  unitReviews: WorkerReviewType[];
  open?: boolean;
  title?: string | React.ReactElement;
};

function UnitReviewsCollapsable(props: UnitReviewsCollapsablePropsType) {
  const { className, open, title, unitReviews } = props;

  const _title = title || "Granted Qualifications";

  return (
    <CollapsableBlock
      className={`unit-reviews ${className || ""}`}
      title={_title}
      open={open}
      tooltip={"Toggle Worker Opinion data"}
    >
      <Table
        className={`unit-reviews-table`}
        responsive={"sm"}
        bordered={false}
      >
        <thead>
          <tr className={`titles-row`}>
            <th className={`title qualification`}>
              <b>Qualification</b>
            </th>
            <th className={`title value`}>
              <b>Value</b>
            </th>
            <th className={`title date`}>
              <b>Date</b>
            </th>
            <th className={`title status`}>
              <b>Unit Action</b>
            </th>
            <th className={`title bonus`}>
              <b>Bonus</b>
            </th>
            <th className={`title blocked`}>
              <b>Worker Action</b>
            </th>
            <th className={`title note`}>
              <b>Note</b>
            </th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {(unitReviews || [].length) &&
            unitReviews.map((unitReview: WorkerReviewType, index: number) => {
              const date = moment(unitReview.creation_date).format(
                DEFAULT_DATE_FORMAT
              );
              const statusColorClass =
                STATUS_COLOR_CLASS_MAPPING[unitReview.status];

              return (
                <tr className={`value-row`} key={"unit-review-row" + index}>
                  <td className={`qualification`}>
                    {unitReview.qualification_name}
                  </td>
                  <td className={`value`}>{unitReview.value}</td>
                  <td className={`date`}>{date}</td>
                  <td
                    className={`
                      status
                      ${statusColorClass ? ` ${statusColorClass}` : ""}
                    `}
                  >
                    {capitalizeString(unitReview.status.replace("_", "-"))}
                  </td>
                  <td className={`bonus`}>{unitReview.bonus}</td>
                  <td className={`blocked`}>
                    {unitReview.blocked_worker ? <b>BLOCKED</b> : ""}
                  </td>

                  <td className={`note`}>{unitReview.review_note}</td>
                  <td></td>
                </tr>
              );
            })}
        </tbody>
      </Table>
    </CollapsableBlock>
  );
}

export default UnitReviewsCollapsable;
