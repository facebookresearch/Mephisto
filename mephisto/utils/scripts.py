#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""
Utilities that are useful for Mephisto-related scripts. 
"""

from mephisto.core.local_database import LocalMephistoDB
from mephisto.core.argparse_parser import str2bool, str2floats, str2none
from mephisto.core.utils import get_mock_requester, get_root_data_dir

import argparse
from typing import Tuple, Dict, Any, TYPE_CHECKING
import os
if TYPE_CHECKING:
    from mephisto.data_model.database import MephistoDB


class MephistoRunScriptParser(argparse.ArgumentParser):
    """
    Parser that adds common options for Mephisto run scripts
    """

    def __init__(self, description="Parser for a mephisto run task"):
        """
        Initialize a parser to extract run options.

        Can register additional arguments with add_options,
        and these will be returned in the namespace returned
        from parse_known_args
        """
        super().__init__(
            description=description,
            allow_abbrev=False,
            conflict_handler='resolve',
        )
        self.register('type', 'nonestr', str2none)
        self.register('type', 'bool', str2bool)
        self.register('type', 'floats', str2floats)
        self.add_requester_args()
        self.add_architect_args()
        self.add_datapath_arg()

    def add_requester_args(self, argument_group=None):
        """
        Add arguments for the requester type
        """
        if argument_group is None:
            argument_group = self
        argument_group.add_argument(
            '-ptype',
            '--provider-type',
            default=None,
            help='Provider type to use',
        )
        argument_group.add_argument(
            '-rname',
            '--requester-name',
            default=None,
            help='Requester name to launch with',
        )

    def add_architect_args(self, argument_group=None):
        """
        Add arguments for the architect
        """
        if argument_group is None:
            argument_group = self
        argument_group.add_argument(
            '-atype',
            '--architect-type',
            default=None,
            help='Architect type to use for launch',
        )

    def add_datapath_arg(self, argument_group=None):
        """
        Add datapath for use with mephisto
        """
        if argument_group is None:
            argument_group = self
        argument_group.add_argument(
            '-dpath',
            '--datapath',
            default=None,
            help='Data path for this mephisto run',
        )

    def parse_launch_arguments(self, args=None) -> Tuple[str, str, "MephistoDB", Dict[str, Any]]:
        """
        Parse common arguments out from the command line, returns a 
        tuple of the architect type, the requester name to use, the
        MephistoDB to run with, and any  additional arguments parsed 
        out by the argument parser

        Defaults to a mock architect with a mock requester with no arguments
        """
        args, _unknown = self.parse_known_args(args=args)
        arg_dict = vars(args)
        requester_name = arg_dict['requester_name']
        provider_type = arg_dict['provider_type']
        architect_type = arg_dict['architect_type']
        datapath = arg_dict['datapath']

        if datapath is None:
            datapath = get_root_data_dir()
        
        database_path = os.path.join(datapath, 'database.db')
        db = LocalMephistoDB(database_path=database_path)

        if requester_name is None:
            if provider_type is None:
                print("No requester specified, defaulting to mock")
                provider_type = 'mock'
            if provider_type == 'mock':
                req = get_mock_requester(db)
                requester_name = req.requester_name
            else:
                reqs = db.find_requesters(provider_type=provider_type)
                # TODO (#93) proper logging
                if len(reqs) == 0:
                    print(
                        f"No requesters found for provider type {provider_type}, please "
                        f"register one. You can register with `mephisto register {provider_type}`, "
                        f"or `python mephisto/client/cli.py register {provider_type}` if you haven't "
                        "installed Mephisto using poetry."
                    )
                    raise AssertionError("No requesters existed for the provided type")
                elif len(reqs) == 1:
                    req = reqs[0]
                    requester_name = req.requester_name
                    print(f"Found one `{provider_type}` requester to launch with: {requester_name}")
                else:
                    req = reqs[-1]
                    requester_name = req.requester_name
                    print(
                        f"Found many `{provider_type}` requesters to launch with, "
                        f"choosing the most recent: {requester_name}"
                    )
        else:
            # Ensure provided requester exists
            reqs = db.find_requesters(requester_name=requester_name)
            if len(reqs) == 0:
                print(
                    f"No requesters found under name {requester_name}, "
                    "have you registered with `mephisto register`?"
                )
            provider_type = reqs[0].provider_type

        # provider type and requester name now set, ensure architect
        if architect_type is None:
            if provider_type == 'mock':
                architect_type = "local"
            elif provider_type == 'mturk_sandbox':
                architect_type = "heroku"
            elif provider_type == 'mturk':
                architect_type = "heroku"
            else: 
                architect_type = "local"

            # TODO (#93) proper logging
            print(
                f"No architect specified, defaulting to architect "
                f"`{architect_type}` for provider `{provider_type}`"
            )
        
        return architect_type, requester_name, db, arg_dict



