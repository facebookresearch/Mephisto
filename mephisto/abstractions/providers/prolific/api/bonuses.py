#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from .base_api_resource import BaseAPIResource
from .base_api_resource import HTTPMethod
from .data_models import BonusPayments


class Bonuses(BaseAPIResource):
    set_up_api_endpoint = "submissions/bonus-payments/"
    pay_api_endpoint = "bulk-bonus-payments/{id}/pay/"

    @classmethod
    def set_up(cls, study_id: str, csv_bonuses: str) -> BonusPayments:
        """
        Set up bonus payments to one or more participants/submissions in a study.
        :param study_id: Study ID
        :param csv_bonuses: String with CSV file text (not a file)
        :return: BonusPayments object
        """
        response_json = cls.post(
            cls.set_up_api_endpoint,
            params=dict(
                study_id=study_id,
                csv_bonuses=csv_bonuses,
            ),
        )
        return BonusPayments(**response_json)

    @classmethod
    def pay(cls, id: str) -> str:
        """
        Bonus payments are made asynchronously.
        The payment will be done in the following minutes and
        your balance will be updated accordingly.
        :param id: Bulk bonus payment ID
        :return: string
        """
        endpoint = cls.pay_api_endpoint.format(id=id)
        method = HTTPMethod.POST
        response = cls._base_request(method, endpoint)
        return response
