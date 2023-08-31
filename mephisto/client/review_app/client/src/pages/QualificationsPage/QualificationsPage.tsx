/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import * as React from 'react';
import { useEffect } from 'react';
import { getQualifications } from 'requests/qualifications';
import './QualificationsPage.css';


const STORAGE_APPROVE_QIALIFICATION_ID_KEY: string = 'approveQualificationID';
const STORAGE_REJECT_QIALIFICATION_ID_KEY: string = 'rejectQualificationID';


function QualificationsPage() {
  const { localStorage } = window;

  const [qualifications, setQualifications] = React.useState<Array<Qualification>>(null);
  const [approveQualificationID, setApproveQualificationID] = React.useState<number>(null);
  const [rejectQualificationID, setRejectQualificationID] = React.useState<number>(null);
  const [loading, setLoading] = React.useState(false);
  const [errors, setErrors] = React.useState<ErrorResponse>(null);

  const localStorageApproveQualificationID = localStorage.getItem(
    STORAGE_APPROVE_QIALIFICATION_ID_KEY
  );
  const localStorageRejectQualificationID = localStorage.getItem(
    STORAGE_REJECT_QIALIFICATION_ID_KEY
  );

  if (!approveQualificationID && localStorageApproveQualificationID) {
    setApproveQualificationID(Number(localStorageApproveQualificationID));
  }

  if (!rejectQualificationID && localStorageRejectQualificationID) {
    setRejectQualificationID(Number(localStorageRejectQualificationID));
  }

  const getQualificationsIDs = (_qualifications: Array<Qualification>): Array<string> => {
    let ids = [];
    _qualifications.map((q: Qualification) => ids.push(q.id));
    return ids;
  }

  const getQualificationByID = (
    _qualifications: Array<Qualification>, id: number | string,
  ): Qualification => {
    for (let q of _qualifications) {
      if (String(q.id) === String(id)) {
        return q;
      }
    }
    return null
  }

  useEffect(() => {
    if (qualifications === null) {
      getQualifications(setQualifications, setLoading, setErrors, null);
    }
  }, []);

  return <div className={'qualifications'}>
    Qualifications:

    {errors && (
      <div>{errors.error}</div>
    )}

    {qualifications && approveQualificationID in getQualificationsIDs(qualifications) && approveQualificationID ? (
      <div>
        Approve qualification: {getQualificationByID(qualifications, approveQualificationID).name}
      </div>
    ) : null}

    {qualifications && rejectQualificationID in getQualificationsIDs(qualifications) && rejectQualificationID ? (
      <div>
        Reject qualification: {getQualificationByID(qualifications, rejectQualificationID).name}
      </div>
    ) : null}

  </div>;
}


export default QualificationsPage;
