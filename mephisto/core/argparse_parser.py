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
from omegaconf import OmegaConf, MISSING, DictConfig
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import fields, Field

def get_dict_from_field(in_field: Field) -> Dict[str, Any]:
    """
    Extract all of the arguments from an argument group
    and return a dict mapping from argument dest to argument dict
    """
    return {
        'dest': in_field.name,
        'type': in_field.type.__name__,
        'default': in_field.default,
        'help': in_field.metadata.get('help'),
        'choices': in_field.metadata.get('choices'),
        'required': in_field.metadata.get('required', False),
    }

def get_extra_argument_dicts(customizable_class: Any) -> List[Dict[str, Any]]:
    """
    Produce the argument dicts for the given customizable class
    (Blueprint, Architect, etc)
    """
    dict_fields = fields(customizable_class.ArgsClass)
    usable_fields = [f for f in dict_fields if not f.name.startswith('_')]
    parsed_fields = [get_dict_from_field(f) for f in usable_fields]
    return [{'desc': '', 'args': {f['dest']: f for f in parsed_fields}}]


def parse_arg_dict(customizable_class: Any, args: Dict[str, Any]) -> DictConfig:
    """
    Get the ArgsClass for a class, then parse the given args using
    it. Return the DictConfig of the finalized namespace.
    """
    return OmegaConf.structured(customizable_class.ArgsClass(**args))

