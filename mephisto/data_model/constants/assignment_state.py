#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from typing import List


class AssignmentState:
    CREATED = "created"
    LAUNCHED = "launched"
    ASSIGNED = "assigned"
    COMPLETED = "completed"
    ACCEPTED = "accepted"
    MIXED = "mixed"
    REJECTED = "rejected"
    SOFT_REJECTED = "soft_rejected"
    EXPIRED = "expired"

    @staticmethod
    def valid() -> List[str]:
        """Return all valid assignment statuses"""
        return [
            AssignmentState.CREATED,
            AssignmentState.LAUNCHED,
            AssignmentState.ASSIGNED,
            AssignmentState.COMPLETED,
            AssignmentState.ACCEPTED,
            AssignmentState.MIXED,
            AssignmentState.REJECTED,
            AssignmentState.SOFT_REJECTED,
            AssignmentState.EXPIRED,
        ]

    @staticmethod
    def incomplete() -> List[str]:
        """Return all statuses that are considered incomplete"""
        return [
            AssignmentState.CREATED,
            AssignmentState.LAUNCHED,
            AssignmentState.ASSIGNED,
        ]

    @staticmethod
    def payable() -> List[str]:
        """Return all statuses that should be considered spent budget"""
        return [
            AssignmentState.LAUNCHED,
            AssignmentState.ASSIGNED,
            AssignmentState.COMPLETED,
            AssignmentState.ACCEPTED,
            AssignmentState.SOFT_REJECTED,
        ]

    @staticmethod
    def valid_unit() -> List[str]:
        """Return all statuses that are valids for a Unit"""
        return [
            AssignmentState.CREATED,
            AssignmentState.LAUNCHED,
            AssignmentState.ASSIGNED,
            AssignmentState.COMPLETED,
            AssignmentState.ACCEPTED,
            AssignmentState.REJECTED,
            AssignmentState.SOFT_REJECTED,
            AssignmentState.EXPIRED,
        ]

    @staticmethod
    def final_unit() -> List[str]:
        """Return all statuses that are terminal for a Unit"""
        return [
            AssignmentState.ACCEPTED,
            AssignmentState.EXPIRED,
            AssignmentState.SOFT_REJECTED,
        ]

    @staticmethod
    def completed() -> List[str]:
        """Return all statuses that denote a unit having been completed"""
        return [
            AssignmentState.COMPLETED,
            AssignmentState.ACCEPTED,
            AssignmentState.REJECTED,
            AssignmentState.SOFT_REJECTED,
        ]

    @staticmethod
    def final_agent() -> List[str]:
        """Return all statuses that are terminal changes to a Unit's agent"""
        return [
            AssignmentState.COMPLETED,
            AssignmentState.ACCEPTED,
            AssignmentState.REJECTED,
            AssignmentState.SOFT_REJECTED,
            AssignmentState.EXPIRED,
        ]
