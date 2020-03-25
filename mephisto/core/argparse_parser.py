#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
The following is a series of functions built to work with argparse
version 1.1. They exist to be able to extract arguments out from
an argparser for usage in other places. This allows Mephisto
to be able to request the correct arguments from the frontend
and construct valid argument strings from user input there.

It relies on underlying implementation details of argparse (ick)
and as such is only guaranteed stable for argparse 1.1
"""

import argparse
from typing import Optional, Dict, Any, List


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


def collect_groups_recurse(group: argparse._ArgumentGroup):
    """
    Recursively traverse an argument group, returning
    the group and all sub-groups.

    Ignores groups without the description attribute set
    """
    pop_list = [group]
    ret_list: List[argparse._ArgumentGroup] = []
    while len(pop_list) > 0:
        cur_group = pop_list.pop()
        ret_list.append(cur_group)
        if len(cur_group._action_groups) > 0:
            pop_list += cur_group._action_groups.copy()
    return [g for g in ret_list if g.description is not None]


def get_argument_groups(
    parser: argparse.ArgumentParser
) -> Dict[str, argparse._ArgumentGroup]:
    """
    Extract all of the groups from an arg parser and
    return a dict mapping from group title to group
    """
    groups: Dict[str, Any] = {"__NO_TITLE__": []}
    all_action_groups: List[argparse._ArgumentGroup] = []
    for group in parser._action_groups:
        all_action_groups += collect_groups_recurse(group)
    for group in all_action_groups:
        if group.title is None:
            groups["__NO_TITLE__"].append(group)
        else:
            groups[group.title] = group
    return groups


def get_arguments_from_group(group: argparse._ArgumentGroup) -> Dict[str, Any]:
    """
    Extract all of the arguments from an argument group
    and return a dict mapping from argument dest to argument dict
    """
    if group.description is None:
        return {}
    parsed_actions = {}
    for action in group._group_actions:
        action_type = action.type
        type_string = None
        if action_type is None:
            type_string = "str"
        elif isinstance(action_type, argparse.FileType):
            type_string = "FileType"
        elif hasattr(action_type, "__name__"):
            type_string = action_type.__name__
        else:
            type_string = "unknown_type"
        parsed_actions[action.dest] = {
            "dest": action.dest,
            "help": action.help,
            "default": action.default,
            "type": type_string,
            "choices": action.choices,
            "option_string": action.option_strings[0],
            "required": action.required,
        }
    return parsed_actions


def get_argument_group_dict(
    group: argparse._ArgumentGroup,
) -> Optional[Dict[str, Any]]:
    """
    Extract an argument group (to be ready to send it to frontend)
    """
    if group.description is None:
        return None
    return {"desc": group.description, "args": get_arguments_from_group(group)}


def get_extra_argument_dicts(customizable_class: Any) -> List[Dict[str, Any]]:
    """
    Produce the argument dicts for the given customizable class
    (Blueprint, Architect, etc)
    """
    dummy_parser = argparse.ArgumentParser()
    arg_group = dummy_parser.add_argument_group("test_arguments")
    customizable_class.add_args_to_group(arg_group)
    groups = collect_groups_recurse(arg_group)
    parsed_groups = [get_argument_group_dict(g) for g in groups]
    return [g for g in parsed_groups if g is not None]


def parse_arg_dict(customizable_class: Any, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get the argparser for a class, then parse the given args using
    it. Return the dict of the finalized namespace.
    """
    final_args = []
    # Extract the expected argument string
    for _key, val in args.items():
        final_args.append(val["option_string"])
        final_args.append(val["value"])

    # Get an argparser with the current class
    dummy_parser = argparse.ArgumentParser()
    arg_group = dummy_parser.add_argument_group("test_arguments")
    customizable_class.add_args_to_group(arg_group)

    # Parse the namespace and return
    arg_namespace = dummy_parser.parse_args(final_args)
    return vars(arg_namespace)


def get_default_arg_dict(customizable_class: Any) -> Dict[str, Any]:
    """
    Produce an opt dict containing the defaults for all
    arguments for the arguments added to the parser
    """
    init_arg_dicts = get_extra_argument_dicts(customizable_class)
    found_opts: Dict[str, Any] = {}
    for arg_group in init_arg_dicts:
        for arg_name, arg_attributes in arg_group["args"].items():
            found_opts[arg_name] = arg_attributes["default"]
    filtered_opts = {k: v for k, v in found_opts.items() if v is not None}
    return filtered_opts
