#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.data_model.constants.assignment_state import AssignmentState
import unittest


class TestDataModel(unittest.TestCase):
    """
    Unit testing for components of the Mephisto Data Model
    """

    def test_ensure_valid_statuses(self):
        """Test that all the statuses are represented"""
        a_state = AssignmentState
        found_valid = a_state.valid()
        SUBARRAYS = {
            "valid": a_state.valid(),
            "incomplete": a_state.incomplete(),
            "payable": a_state.payable(),
            "valid_unit": a_state.valid_unit(),
            "final_unit": a_state.final_unit(),
            "completed": a_state.completed(),
            "final_agent": a_state.final_agent(),
        }
        found_keys = [k for k in dir(a_state) if k.upper() == k]
        found_vals = [getattr(a_state, k) for k in found_keys]
        for v in found_vals:
            self.assertIn(
                v, found_valid, f"Expected to find {v} in valid list {found_valid}"
            )
        for sublist, found_array in SUBARRAYS.items():
            for v in found_array:
                self.assertIn(
                    v,
                    found_vals,
                    f"Expected to find {v} from {sublist} in "
                    f"{a_state} attributes, not in {found_vals}",
                )


if __name__ == "__main__":
    unittest.main()
