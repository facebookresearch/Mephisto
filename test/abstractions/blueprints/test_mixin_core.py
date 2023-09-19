#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
import tempfile
import os
import shutil

from omegaconf import OmegaConf
from dataclasses import dataclass

from mephisto.data_model.task_run import TaskRun, TaskRunArgs
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.abstractions.blueprint import (
    Blueprint,
    BlueprintMixin,
    BlueprintArgs,
    SharedTaskState,
)
from mephisto.utils.testing import get_test_task_run
from mephisto.abstractions.architects.mock_architect import (
    MockArchitect,
    MockArchitectArgs,
)
from mephisto.operations.hydra_config import MephistoConfig
from mephisto.abstractions.providers.mock.mock_provider import MockProviderArgs
from mephisto.abstractions.blueprints.mock.mock_blueprint import MockBlueprintArgs

from typing import List, Dict, ClassVar, Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from omegaconf import DictConfig


class BrokenMixin(BlueprintMixin):
    """Mixin that fails to define ArgsMixin or SharedStateMixin"""

    def init_mixin_config(
        self, task_run: "TaskRun", args: "DictConfig", shared_state: "SharedTaskState"
    ) -> None:
        return

    @classmethod
    def assert_mixin_args(cls, args: "DictConfig", shared_state: "SharedTaskState") -> None:
        return

    @classmethod
    def get_mixin_qualifications(
        cls, args: "DictConfig", shared_state: "SharedTaskState"
    ) -> List[Dict[str, Any]]:
        return []


@dataclass
class ArgsMixin1:
    arg1: int = 0


@dataclass
class StateMixin1:
    arg1: int = 0


class MockBlueprintMixin1(BlueprintMixin):
    MOCK_QUAL_NAME = "mock_mixin_one"
    ArgsMixin: ClassVar[Any] = ArgsMixin1
    SharedStateMixin: ClassVar[Any] = StateMixin1
    mixin_init_calls: int

    def init_mixin_config(
        self, task_run: "TaskRun", args: "DictConfig", shared_state: "SharedTaskState"
    ) -> None:
        if hasattr(self, "mixin_init_calls"):
            self.mixin_init_calls += 1
        else:
            self.mixin_init_calls = 1

    @classmethod
    def assert_mixin_args(cls, args: "DictConfig", shared_state: "SharedTaskState") -> None:
        assert args.blueprint.arg1 == 0, "Was not the default value of arg1"

    @classmethod
    def get_mixin_qualifications(
        cls, args: "DictConfig", shared_state: "SharedTaskState"
    ) -> List[Dict[str, Any]]:
        return [{"qual_name": cls.MOCK_QUAL_NAME}]


@dataclass
class ArgsMixin2:
    arg2: int = 0


@dataclass
class StateMixin2:
    arg2: int = 0


class MockBlueprintMixin2(BlueprintMixin):
    MOCK_QUAL_NAME = "mock_mixin_two"
    ArgsMixin: ClassVar[Any] = ArgsMixin2
    SharedStateMixin: ClassVar[Any] = StateMixin2
    mixin_init_calls: int

    def init_mixin_config(
        self, task_run: "TaskRun", args: "DictConfig", shared_state: "SharedTaskState"
    ) -> None:
        if hasattr(self, "mixin_init_calls"):
            self.mixin_init_calls += 1
        else:
            self.mixin_init_calls = 1

    @classmethod
    def assert_mixin_args(cls, args: "DictConfig", shared_state: "SharedTaskState") -> None:
        assert args.blueprint.arg2 == 0, "Was not the default value of arg2"

    @classmethod
    def get_mixin_qualifications(
        cls, args: "DictConfig", shared_state: "SharedTaskState"
    ) -> List[Dict[str, Any]]:
        return [{"qual_name": cls.MOCK_QUAL_NAME}]


@dataclass
class ComposedArgsMixin(ArgsMixin1, ArgsMixin2):
    pass


@dataclass
class ComposedStateMixin(StateMixin1, StateMixin2):
    pass


class ComposedMixin(MockBlueprintMixin1, MockBlueprintMixin2):
    MOCK_QUAL_NAME = "mock_mixin_mixed"
    ArgsMixin = ComposedArgsMixin
    SharedStateMixin = ComposedStateMixin
    mixin_init_calls: int

    @classmethod
    def assert_mixin_args(cls, args: "DictConfig", shared_state: "SharedTaskState") -> None:
        MockBlueprintMixin1.assert_mixin_args(args, shared_state)
        MockBlueprintMixin2.assert_mixin_args(args, shared_state)


class TestBlueprintMixinCore(unittest.TestCase):
    """Test the functionality underlying blueprint mixins that allow them to work"""

    def get_structured_config(self, blueprint_args):
        config = MephistoConfig(
            blueprint=blueprint_args,
            provider=MockProviderArgs(requester_name="mock_requester"),
            architect=MockArchitectArgs(should_run_server=False),
            task=TaskRunArgs(
                task_title="title",
                task_description="This is a description",
                task_reward="0.3",
                task_tags="1,2,3",
                maximum_units_per_worker=2,
                allowed_concurrent=1,
                task_name="max-unit-test",
            ),
        )
        return OmegaConf.structured(config)

    def setUp(self) -> None:
        self.data_dir = tempfile.mkdtemp()
        database_path = os.path.join(self.data_dir, "mephisto.db")
        self.db = LocalMephistoDB(database_path)
        self.task_run = TaskRun.get(self.db, get_test_task_run(self.db))

    def tearDown(self) -> None:
        self.db.shutdown()
        shutil.rmtree(self.data_dir)

    def test_broken_mixin(self):
        class TestBlueprint(BrokenMixin, Blueprint):
            def get_initialization_data(self):
                return []

        args = TestBlueprint.ArgsClass()
        shared_state = TestBlueprint.SharedStateClass()
        cfg = self.get_structured_config(args)

        with self.assertRaises(AttributeError, msg="Undefined mixin classes should fail here"):

            @BrokenMixin.mixin_args_and_state
            class TestBlueprint(BrokenMixin, Blueprint):
                def get_initialization_data(self):
                    return []

    def test_working_mixin(self):
        class TestBlueprint(MockBlueprintMixin1, Blueprint):
            def get_initialization_data(self):
                return []

        args = TestBlueprint.ArgsClass()
        shared_state = TestBlueprint.SharedStateClass()
        cfg = self.get_structured_config(args)
        with self.assertRaises(Exception, msg="Class should not have correct args"):
            TestBlueprint.assert_task_args(cfg, shared_state)

        # Working mixin by manually creating classes
        @dataclass
        class TestArgs(ArgsMixin1, BlueprintArgs):
            pass

        @dataclass
        class TestState(StateMixin1, SharedTaskState):
            pass

        class TestBlueprint(MockBlueprintMixin1, Blueprint):
            ArgsClass = TestArgs
            SharedStateClass = TestState

            def get_initialization_data(self):
                return []

        args = TestBlueprint.ArgsClass()
        shared_state = TestBlueprint.SharedStateClass()
        cfg = self.get_structured_config(args)
        TestBlueprint.assert_task_args(cfg, shared_state)
        blueprint = TestBlueprint(self.task_run, cfg, shared_state)
        self.assertEqual(blueprint.mixin_init_calls, 1, "More than one mixin init call!")

        # Working mixin using the decorator
        @MockBlueprintMixin1.mixin_args_and_state
        class TestBlueprint(MockBlueprintMixin1, Blueprint):
            def get_initialization_data(self):
                return []

        args = TestBlueprint.ArgsClass()
        shared_state = TestBlueprint.SharedStateClass()
        cfg = self.get_structured_config(args)
        TestBlueprint.assert_task_args(cfg, shared_state)
        blueprint = TestBlueprint(self.task_run, cfg, shared_state)
        self.assertEqual(blueprint.mixin_init_calls, 1, "More than one mixin init call!")

    def test_mixin_multi_inheritence(self):
        @MockBlueprintMixin1.mixin_args_and_state
        @MockBlueprintMixin2.mixin_args_and_state
        class DoubleMixinBlueprint(MockBlueprintMixin1, MockBlueprintMixin2, Blueprint):
            def get_initialization_data(self):
                return []

        args = DoubleMixinBlueprint.ArgsClass()
        shared_state = DoubleMixinBlueprint.SharedStateClass()
        cfg = self.get_structured_config(args)
        DoubleMixinBlueprint.assert_task_args(cfg, shared_state)
        blueprint = DoubleMixinBlueprint(self.task_run, cfg, shared_state)
        self.assertEqual(blueprint.mixin_init_calls, 2, "Should have 2 mixin calls")

        # Ensure qualifications are correct
        required_quals = DoubleMixinBlueprint.get_required_qualifications(args, shared_state)
        self.assertEqual(len(BlueprintMixin.extract_unique_mixins(DoubleMixinBlueprint)), 2)
        qual_names = [q["qual_name"] for q in required_quals]
        self.assertIn(MockBlueprintMixin1.MOCK_QUAL_NAME, qual_names)
        self.assertIn(MockBlueprintMixin2.MOCK_QUAL_NAME, qual_names)

        # Check functionality of important helpers
        self.assertEqual(len(BlueprintMixin.extract_unique_mixins(DoubleMixinBlueprint)), 2)

        # Ensure failures work for each of the arg failures
        shared_state = DoubleMixinBlueprint.SharedStateClass()
        args = DoubleMixinBlueprint.ArgsClass(arg1=2)
        cfg = self.get_structured_config(args)
        with self.assertRaises(AssertionError, msg="Should have called both asserts"):
            DoubleMixinBlueprint.assert_task_args(cfg, shared_state)
        args = DoubleMixinBlueprint.ArgsClass(arg2=2)
        print(args)
        cfg = self.get_structured_config(args)
        with self.assertRaises(AssertionError, msg="Should have called both asserts"):
            DoubleMixinBlueprint.assert_task_args(cfg, shared_state)

    def test_composed_mixin_inheritence(self):
        @ComposedMixin.mixin_args_and_state
        class ComposedBlueprint(ComposedMixin, MockBlueprintMixin1, Blueprint):
            def get_initialization_data(self):
                return []

        args = ComposedBlueprint.ArgsClass()
        shared_state = ComposedBlueprint.SharedStateClass()
        cfg = self.get_structured_config(args)
        ComposedBlueprint.assert_task_args(cfg, shared_state)
        blueprint = ComposedBlueprint(self.task_run, cfg, shared_state)
        self.assertEqual(blueprint.mixin_init_calls, 1, "Should have 1 mixin call")

        # Ensure qualifications are correct
        required_quals = ComposedBlueprint.get_required_qualifications(args, shared_state)
        self.assertEqual(len(BlueprintMixin.extract_unique_mixins(ComposedBlueprint)), 1)
        qual_names = [q["qual_name"] for q in required_quals]
        self.assertIn(ComposedBlueprint.MOCK_QUAL_NAME, qual_names)

        # Check functionality of important helpers
        self.assertEqual(len(BlueprintMixin.extract_unique_mixins(ComposedBlueprint)), 1)

        # Ensure failures work for each of the arg failures
        shared_state = ComposedBlueprint.SharedStateClass()
        args = ComposedBlueprint.ArgsClass(arg1=2)
        cfg = self.get_structured_config(args)
        with self.assertRaises(AssertionError, msg="Should have called both asserts"):
            ComposedBlueprint.assert_task_args(cfg, shared_state)
        args = ComposedBlueprint.ArgsClass(arg2=2)
        cfg = self.get_structured_config(args)
        with self.assertRaises(AssertionError, msg="Should have called both asserts"):
            ComposedBlueprint.assert_task_args(cfg, shared_state)


if __name__ == "__main__":
    unittest.main()
