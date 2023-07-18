#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Type, TypeVar, cast

from .base_api_resource import BaseAPIResource
from .bonuses import Bonuses as _Bonuses
from .eligibility_requirements import (
    EligibilityRequirements as _EligibilityRequirements,
)
from .invitations import Invitations as _Invitations
from .messages import Messages as _Messages
from .participant_groups import ParticipantGroups as _ParticipantGroups
from .projects import Projects as _Projects
from .studies import Studies as _Studies
from .submissions import Submissions as _Submissions
from .users import Users as _Users
from .workspaces import Workspaces as _Workspaces

T = TypeVar("T")


def wrap_class(target_cls: Type[T], api_key: str) -> Type[T]:
    """
    Create a wrapper around the given BaseAPIResource to have the
    api_key pre-bound
    """
    assert issubclass(target_cls, BaseAPIResource), "Can only wrap BaseAPIResource"

    class Wrapper(target_cls):
        @classmethod
        def _base_request(cls, *args, **kwargs):
            new_args = {k: v for k, v in kwargs.items()}
            if new_args.get("api_key", None) is None:
                new_args["api_key"] = api_key
            return super()._base_request(*args, **new_args)

    # Name wrapper after wrapped class (for logging)
    Wrapper.__name__ = target_cls.__name__

    return cast(Type[T], Wrapper)


class ProlificClient:

    Bonuses: Type[_Bonuses]
    EligibilityRequirements: Type[_EligibilityRequirements]
    Invitations: Type[_Invitations]
    Messages: Type[_Messages]
    ParticipantGroups: Type[_ParticipantGroups]
    Projects: Type[_Projects]
    Studies: Type[_Studies]
    Submissions: Type[_Submissions]
    Users: Type[_Users]
    Workspaces: Type[_Workspaces]

    def __init__(self, api_key: str):
        """
        Creates a client that can be used to call all of the
        prolific data model using the provided key.
        """
        self.Bonuses = wrap_class(_Bonuses, api_key)
        self.EligibilityRequirements = wrap_class(_EligibilityRequirements, api_key)
        self.Invitations = wrap_class(_Invitations, api_key)
        self.Messages = wrap_class(_Messages, api_key)
        self.ParticipantGroups = wrap_class(_ParticipantGroups, api_key)
        self.Projects = wrap_class(_Projects, api_key)
        self.Studies = wrap_class(_Studies, api_key)
        self.Submissions = wrap_class(_Submissions, api_key)
        self.Users = wrap_class(_Users, api_key)
        self.Workspaces = wrap_class(_Workspaces, api_key)
