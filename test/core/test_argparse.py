#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from mephisto.core.argparse_parser import (
    collect_groups_recurse,
    get_argument_groups,
    get_arguments_from_group,
    get_argument_group_dict,
    get_extra_argument_dicts,
    parse_arg_dict,
    get_default_arg_dict,
)
import argparse
from argparse import _ArgumentGroup as ArgumentGroup


class MockCustomizableClass:
    """
    Mock class with supposed customizability, for argparsing purposes
    """

    TEST_DESCRIPTION = "This is a test description"
    TEST_SUBGROUP_DESCRIPTION = "This is a test subgroup description"
    ARGUMENT_FLAG = "--test-arg"
    ARGUMENT_NAME = "test_arg"
    ARGUMENT_TYPE = bool
    DEFAULT_FLAG = "--default-arg"
    DEFAULT_NAME = "default_arg"
    DEFAULT_TYPE = int
    DEFAULT_VALUE = 3

    def __init__(self):
        pass

    @classmethod
    def add_args_to_group(cls, group: ArgumentGroup):
        group.description = cls.TEST_DESCRIPTION
        group.add_argument(
            cls.ARGUMENT_FLAG, dest=cls.ARGUMENT_NAME, type=cls.ARGUMENT_TYPE
        )
        subgroup = group.add_argument_group("test_subgroup")
        subgroup.description = cls.TEST_SUBGROUP_DESCRIPTION
        subgroup.add_argument(
            cls.DEFAULT_FLAG,
            dest=cls.DEFAULT_NAME,
            type=cls.DEFAULT_TYPE,
            default=cls.DEFAULT_VALUE,
        )


class MockUncustomizableClass:
    """
    Mock class with no customizability, for argparsing purposes
    """

    TEST_DESCRIPTION = "This is a test description"

    def __init__(self):
        pass

    @classmethod
    def add_args_to_group(cls, group: ArgumentGroup):
        group.add_argument(
            "--hidden-default-argument", dest="hidden_default_argument", default=3
        )
        group.add_argument("--hidden-argument", dest="hidden_argument")


class TestArgparseParser(unittest.TestCase):
    """
    Unit testing for the LocalMephistoDB

    Inherits all tests directly from BaseDataModelTests, and
    writes no additional tests.
    """

    def setUp(self) -> None:
        self.argparser = argparse.ArgumentParser()
        self.test_group = self.argparser.add_argument_group("test_group")

    def test_argparse_version(self) -> None:
        """Ensure the argparse version is supported"""
        SUPPORTED_ARGPARSERS = ["1.1"]
        self.assertIn(argparse.__version__, SUPPORTED_ARGPARSERS)  # type: ignore

    def test_collect_groups_recurse(self) -> None:
        """Ensure group collection works as intended"""
        _cls = MockCustomizableClass
        _cls.add_args_to_group(self.test_group)
        groups = collect_groups_recurse(self.test_group)
        self.assertEqual(
            len(groups), 2, f"Groups were not recursively selected, {len(groups)} found"
        )
        group_descriptions = [g.description for g in groups]
        self.assertIn(
            _cls.TEST_DESCRIPTION, group_descriptions, "Expected group is missing"
        )
        self.assertIn(
            _cls.TEST_SUBGROUP_DESCRIPTION,
            group_descriptions,
            "Expected subgroup is missing",
        )

    def test_collect_groups_recurse_empty(self) -> None:
        """Ensure non-described groups are ignored"""
        MockUncustomizableClass.add_args_to_group(self.test_group)
        groups = collect_groups_recurse(self.test_group)
        self.assertEqual(len(groups), 0, "Group found when no described group exists")

    def test_get_argument_groups(self) -> None:
        """Ensure argument groups are retrieved from parsers"""
        MockCustomizableClass.add_args_to_group(self.test_group)
        group_dict = get_argument_groups(self.argparser)
        self.assertEqual(len(group_dict), 3, f"Expected 3 groups, found {group_dict}")
        self.assertEqual(
            len(group_dict["__NO_TITLE__"]),  # type: ignore
            0,
            f"Expected no unnamed groups, found {group_dict['__NO_TITLE__']}.",
        )
        self.assertIn("test_group", group_dict.keys(), "test group not found")
        self.assertIn("test_subgroup", group_dict.keys(), "test subgroup not found")
        self.assertIn(self.test_group, group_dict.values(), "test group doesn't match")

    def test_get_argument_groups_empty(self) -> None:
        """Ensure no argument groups are retrieved from empty parsers"""
        MockUncustomizableClass.add_args_to_group(self.test_group)
        group_dict = get_argument_groups(self.argparser)
        self.assertEqual(len(group_dict), 1, f"Expected 1 group, found {group_dict}")
        self.assertEqual(
            len(group_dict["__NO_TITLE__"]),  # type: ignore
            0,
            f"Expected no unnamed groups, found {group_dict['__NO_TITLE__']}.",
        )

    def test_get_arguments_from_group(self) -> None:
        """Ensure arguments are retrieved from a group, but not subgroups"""
        MockCustomizableClass.add_args_to_group(self.test_group)
        args = get_arguments_from_group(self.test_group)
        self.assertEqual(
            len(args),
            1,
            f"Arguments were not properly selected, expected 1 but, {args} found",
        )
        self.assertIn(MockCustomizableClass.ARGUMENT_NAME, args)

        # Ensure members are set as expected
        test_arg = args[MockCustomizableClass.ARGUMENT_NAME]
        print(test_arg)
        self.assertEqual(test_arg["dest"], MockCustomizableClass.ARGUMENT_NAME)
        self.assertEqual(test_arg["option_string"], MockCustomizableClass.ARGUMENT_FLAG)
        self.assertEqual(test_arg["type"], MockCustomizableClass.ARGUMENT_TYPE.__name__)
        self.assertEqual(test_arg["default"], None)

    def test_get_arguments_from_group_empty(self) -> None:
        """Groups with no description should be skipped"""
        MockUncustomizableClass.add_args_to_group(self.test_group)
        args = get_arguments_from_group(self.test_group)
        self.assertEqual(
            len(args),
            0,
            f"Arguments were not properly selected, expected 0 but, {args} found",
        )

    def test_get_argument_group_dict(self) -> None:
        """Ensure argument group dict creation is as expected"""
        MockCustomizableClass.add_args_to_group(self.test_group)
        group_as_dict = get_argument_group_dict(self.test_group)
        self.assertIsNotNone(group_as_dict)
        assert group_as_dict is not None
        self.assertEqual(group_as_dict["desc"], MockCustomizableClass.TEST_DESCRIPTION)
        self.assertDictEqual(
            group_as_dict["args"], get_arguments_from_group(self.test_group)
        )

    def test_get_argument_group_dict_empty(self) -> None:
        """Ensure empty argument group dict creation is as expected"""
        MockUncustomizableClass.add_args_to_group(self.test_group)
        group_as_dict = get_argument_group_dict(self.test_group)
        self.assertIsNone(group_as_dict)

    def test_get_extra_argument_dicts(self) -> None:
        """
        Ensure it's possible to collect the complete set of arguments
        from a class's extra options
        """
        arg_dicts = get_extra_argument_dicts(MockCustomizableClass)
        self.assertEqual(len(arg_dicts), 2, "Expecting 2 argument groups")
        for arg_dict in arg_dicts:
            self.assertEqual(
                len(arg_dict["args"]),
                1,
                f"Each group should have 1 arg in this test: {arg_dict}",
            )
            self.assertIn(
                arg_dict["desc"],
                [
                    MockCustomizableClass.TEST_DESCRIPTION,
                    MockCustomizableClass.TEST_SUBGROUP_DESCRIPTION,
                ],
                f"Found argument group was not as expected: {arg_dict}",
            )

    def test_get_extra_argument_dicts_empty(self) -> None:
        """Ensure that classes with no arguments produce an empty list"""
        arg_dicts = get_extra_argument_dicts(MockUncustomizableClass)
        self.assertEqual(len(arg_dicts), 0, "Expecting no argument groups")

    def test_parse_arg_dict(self) -> None:
        """
        Ensure that it's possible to parse an argument string
        for a class via argparse
        """
        _cls = MockCustomizableClass
        args_to_parse = {
            _cls.ARGUMENT_NAME: {"option_string": _cls.ARGUMENT_FLAG, "value": False}
        }
        parsed_args = parse_arg_dict(_cls, args_to_parse)
        self.assertEqual(parsed_args[_cls.ARGUMENT_NAME], False)
        self.assertEqual(parsed_args[_cls.DEFAULT_NAME], _cls.DEFAULT_VALUE)

    def test_parse_arg_dict_empty(self) -> None:
        """
        Ensure that parsing over an empty parser is okay, but maintains hidden args
        """
        _cls = MockUncustomizableClass
        # Assert non-existent args fail
        args_to_parse = {"fake_name": {"option_string": "--fake-flag", "value": False}}
        with self.assertRaises(Exception):
            parsed_args = parse_arg_dict(_cls, args_to_parse)

        # Assert empty args are okay
        args_to_parse = {}
        parsed_args = parse_arg_dict(_cls, args_to_parse)

        # Check for hidden flags
        self.assertEqual(
            len(parsed_args),
            2,
            f"Expected 2 hidden argument to be parsed: {parsed_args}",
        )
        self.assertEqual(parsed_args["hidden_default_argument"], 3)
        self.assertIsNone(parsed_args["hidden_argument"])

        # Check for overriding hidden arguments
        args_to_parse = {
            "hidden_argument": {"option_string": "--hidden-argument", "value": "test"}
        }
        parsed_args = parse_arg_dict(_cls, args_to_parse)
        self.assertEqual(len(parsed_args), 2, "Expected hidden arguments to be parsed")
        self.assertEqual(parsed_args["hidden_argument"], "test")

    def test_get_default_arg_dict(self) -> None:
        """Ensure it's possible to get a default argument dict"""
        default_dict = get_default_arg_dict(MockCustomizableClass)
        self.assertEqual(len(default_dict), 1, "Only args with defaults should show")
        default_arg = default_dict[MockCustomizableClass.DEFAULT_NAME]
        self.assertEqual(default_arg, MockCustomizableClass.DEFAULT_VALUE)

    def test_get_default_arg_dict_empty(self) -> None:
        """Ensure no arguments are retrieved (not even hidden) for empty opts"""
        default_dict = get_default_arg_dict(MockUncustomizableClass)
        self.assertEqual(len(default_dict), 0, "No hidden args should show")


if __name__ == "__main__":
    unittest.main()
