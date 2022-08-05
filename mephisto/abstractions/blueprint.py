#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from abc import ABC, abstractmethod
import csv
from genericpath import exists
import os
from rich import print
from typing import (
    ClassVar,
    List,
    Dict,
    Any,
    Optional,
    Type,
    Union,
    Iterable,
    Callable,
    TYPE_CHECKING,
)
from dataclasses import dataclass, field
from omegaconf import MISSING, DictConfig

from mephisto.abstractions._subcomponents.task_builder import TaskBuilder
from mephisto.abstractions._subcomponents.task_runner import TaskRunner
from mephisto.abstractions._subcomponents.agent_state import AgentState
from mephisto.utils.dirs import get_run_file_dir, get_tasks_dir

if TYPE_CHECKING:
    from mephisto.data_model.task_run import TaskRun
    from mephisto.data_model.assignment import InitializationData
    from mephisto.data_model.unit import Unit
    from mephisto.data_model.worker import Worker

from mephisto.utils.logger_core import get_logger

logger = get_logger(name=__name__)


@dataclass
class BlueprintArgs:
    _blueprint_type: str = MISSING
    block_qualification: str = field(
        default=MISSING,
        metadata={
            "help": ("Specify the name of a qualification used to soft block workers.")
        },
    )
    tips_location: str = field(
        default=os.path.join(get_run_file_dir(), "assets/tips.csv"),
        metadata={
            "help": "Path to csv file containing tips",
            "required": False,
        },
    )


@dataclass
class SharedTaskState:
    """
    Base class for specifying additional state that can't just
    be passed as Hydra args, like functions and objects
    """

    task_config: Dict[str, Any] = field(
        default_factory=dict,
        metadata={
            "help": (
                "Values to be included in the frontend MephistoTask.task_config object"
            ),
            "type": "Dict[str, Any]",
            "default": "{}",
        },
    )
    qualifications: List[Any] = field(
        default_factory=list,
        metadata={
            "help": (
                "List of qualification dicts of the form returned by "
                "mephisto.utils.qualifications.make_qualification_dict "
                "to be used with this task run."
            ),
            "type": "List[Dict]",
            "default": "[]",
        },
    )
    worker_can_do_unit: Callable[["Worker", "Unit"], bool] = field(
        default_factory=lambda: (lambda worker, unit: True),
        metadata={
            "help": ("Function to evaluate if a worker is eligible for a given unit"),
            "type": "Callable[[Worker, Unit], bool]",
            "default": "Returns True always",
        },
    )
    on_unit_submitted: Callable[["Unit"], None] = field(
        default_factory=lambda: (lambda unit: None),
        metadata={
            "help": ("Function to evaluate on every unit completed or disconnected"),
            "type": "Callable[[Unit], None]",
            "default": "No-op function",
        },
    )


class BlueprintMixin(ABC):
    """
    Base class for compositional mixins for blueprints

    We expect mixins that subclass other mixins to handle subinitialization
    work, such that only the highest class needs to be called.
    """

    # @property
    # @abstractmethod
    # def ArgsMixin(self) -> Type[object]:  # Should be a dataclass, to extend BlueprintArgs
    #     pass

    # @property
    # @abstractmethod
    # def SharedStateMixin(
    #     self,
    # ) -> Type[object]:  # Also should be a dataclass, to extend SharedTaskState
    #     pass
    ArgsMixin: ClassVar[Type[object]]
    SharedStateMixin: ClassVar[Type[object]]

    @staticmethod
    def extract_unique_mixins(blueprint_class: Type["Blueprint"]):
        """Return the unique mixin classes that are used in the given blueprint class"""
        mixin_subclasses = [
            clazz
            for clazz in blueprint_class.mro()
            if issubclass(clazz, BlueprintMixin)
        ]
        target_class: Union[Type["Blueprint"], Type["BlueprintMixin"]] = blueprint_class
        # Remove magic created with `mixin_args_and_state`
        while target_class.__name__ == "MixedInBlueprint":
            target_class = mixin_subclasses.pop(0)
        removed_locals = [
            clazz
            for clazz in mixin_subclasses
            if "MixedInBlueprint" not in clazz.__name__
        ]
        filtered_subclasses = set(
            clazz
            for clazz in removed_locals
            if clazz != BlueprintMixin and clazz != target_class
        )

        # Remaining "Blueprints" should be dropped at this point.
        filtered_out_blueprints = set(
            clazz for clazz in filtered_subclasses if not issubclass(clazz, Blueprint)
        )

        # we also want to make sure that we don't double-count extensions of mixins, so remove classes that other classes are subclasses of
        def is_subclassed(clazz):
            return True in [
                issubclass(x, clazz) and x != clazz for x in filtered_out_blueprints
            ]

        unique_subclasses = [
            clazz for clazz in filtered_out_blueprints if not is_subclassed(clazz)
        ]
        return unique_subclasses

    @abstractmethod
    def init_mixin_config(
        self, task_run: "TaskRun", args: "DictConfig", shared_state: "SharedTaskState"
    ) -> None:
        """Method to initialize any required attributes to make this mixin function"""
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def assert_mixin_args(
        cls, args: "DictConfig", shared_state: "SharedTaskState"
    ) -> None:
        """Method to validate the incoming args and throw if something won't work"""
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def get_mixin_qualifications(
        cls, args: "DictConfig", shared_state: "SharedTaskState"
    ) -> List[Dict[str, Any]]:
        """Method to provide any required qualifications to make this mixin function"""
        raise NotImplementedError()

    @classmethod
    def mixin_args_and_state(
        mixin_cls: Type["BlueprintMixin"], target_cls: Type["Blueprint"]
    ):
        """
        Magic utility decorator that can be used to inject mixin configurations
        (BlueprintArgs and SharedTaskState) without the user needing to define new
        classes for these. Should only be used by tasks that aren't already specifying
        new versions of these, which should just inherit otherwise.

        Usage:
          @register_mephisto_abstraction()
          @ABlueprintMixin.mixin_args_and_state
          class MyBlueprint(ABlueprintMixin, Blueprint):
              pass
        """
        # Ignore typing on most of this, as mypy is not able to parse what's happening
        @dataclass
        class MixedInArgsClass(mixin_cls.ArgsMixin, target_cls.ArgsClass):  # type: ignore
            pass

        @dataclass
        class MixedInSharedStateClass(
            mixin_cls.SharedStateMixin, target_cls.SharedStateClass  # type: ignore
        ):
            pass

        class MixedInBlueprint(target_cls):  # type: ignore
            ArgsClass = MixedInArgsClass
            SharedStateClass = MixedInSharedStateClass

        return MixedInBlueprint


class Blueprint(ABC):
    """
    Configuration class for the various parts of building, launching,
    and running a task of a specific task. Provides utility functions
    for managing between the three main components, which are separated
    into separate classes in acknowledgement that some tasks may have
    particularly complicated processes for them
    """

    AgentStateClass: ClassVar[Type["AgentState"]]
    OnboardingAgentStateClass: ClassVar[Type["AgentState"]] = AgentState  # type: ignore
    TaskRunnerClass: ClassVar[Type["TaskRunner"]]
    TaskBuilderClass: ClassVar[Type["TaskBuilder"]]
    ArgsClass: ClassVar[Type["BlueprintArgs"]] = BlueprintArgs
    SharedStateClass: ClassVar[Type["SharedTaskState"]] = SharedTaskState
    BLUEPRINT_TYPE: str

    def __init__(
        self, task_run: "TaskRun", args: "DictConfig", shared_state: "SharedTaskState"
    ):
        self.args = args
        self.shared_state = shared_state
        self.frontend_task_config = shared_state.task_config
        # We automatically call all mixins `init_mixin_config` methods available.
        mixin_subclasses = BlueprintMixin.extract_unique_mixins(self.__class__)
        for clazz in mixin_subclasses:
            clazz.init_mixin_config(self, task_run, args, shared_state)

    @classmethod
    def get_required_qualifications(
        cls, args: DictConfig, shared_state: "SharedTaskState"
    ):
        quals = []
        for clazz in BlueprintMixin.extract_unique_mixins(cls):
            quals += clazz.get_mixin_qualifications(args, shared_state)
        return quals

    @classmethod
    def assert_task_args(cls, args: DictConfig, shared_state: "SharedTaskState"):
        """
        Assert that the provided arguments are valid. Should
        fail if a task launched with these arguments would
        not work
        """
        # We automatically call all mixins `assert_task_args` methods available.
        mixin_subclasses = BlueprintMixin.extract_unique_mixins(cls)
        for clazz in mixin_subclasses:
            clazz.assert_mixin_args(args, shared_state)
        return

    def get_frontend_args(self) -> Dict[str, Any]:
        """
        Specifies what options should be fowarded
        to the client for use by the task's frontend
        """
        self.update_task_config_with_tips(self.frontend_task_config)
        return self.frontend_task_config.copy()

    def get_tips_directory(self) -> Optional[str]:
        """
        Returns the tips directory as set in hydra config
        By default this is '${task_dir}/outputs/tips'
        """
        if "tips_location" in self.args.blueprint:
            path_to_tips = self.args.blueprint.tips_location
            if exists(path_to_tips):
                return path_to_tips
        return None

    def update_task_config_with_tips(
        self,
        frontend_task_config: Dict[str, Any],
    ):
        """
        Updates the frontend args with accepted tips list
        """
        tips: List[Dict[str, Any]] = []
        path_to_tips = self.get_tips_directory()
        if path_to_tips is not None:
            with open(path_to_tips) as tips_file:
                reader = csv.reader(tips_file)
                is_csv_empty = os.stat(path_to_tips).st_size == 0
                if is_csv_empty == False:
                    heading = next(tips_file)
                    headers = heading.split(",")
                    tips_header_index = headers.index("header")
                    tips_text_index = headers.index("text")
                    for row in reader:
                        tips_obj = {}
                        tips_obj["header"] = row[tips_header_index]
                        tips_obj["text"] = row[tips_text_index]
                        tips.append(tips_obj)

            frontend_task_config.update({"tips": tips})

        return frontend_task_config

    @abstractmethod
    def get_initialization_data(
        self,
    ) -> Iterable["InitializationData"]:
        """
        Get all of the data used to initialize tasks from this blueprint.
        Can either be a simple iterable if all the assignments can
        be processed at once, or a Generator if the number
        of tasks is unknown or changes based on something running
        concurrently with the job.
        """
        raise NotImplementedError
