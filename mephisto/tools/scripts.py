#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""
Utilities that are useful for Mephisto-related scripts.
"""

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.abstractions.providers.mturk.mturk_utils import try_prerun_cleanup
from mephisto.operations.operator import Operator
from mephisto.abstractions.databases.local_singleton_database import MephistoSingletonDB
from mephisto.utils.logger_core import format_loud
from mephisto.utils.testing import get_mock_requester
from mephisto.utils.dirs import get_root_data_dir, get_run_file_dir
from mephisto.operations.hydra_config import (
    build_default_task_config,
    register_script_config,
    TaskConfig,
)
from rich.markdown import Markdown
from mephisto.utils.rich import console
from omegaconf import DictConfig, OmegaConf
import functools
import hydra
import subprocess
from typing import (
    List,
    Tuple,
    Any,
    Type,
    TypeVar,
    Callable,
    Optional,
    cast,
    TYPE_CHECKING,
)
import os
from rich import print

if TYPE_CHECKING:
    from mephisto.abstractions.database import MephistoDB


def load_db_and_process_config(
    cfg: DictConfig, print_config=False
) -> Tuple["MephistoDB", DictConfig]:
    """
    Using a Hydra DictConfig built from a TaskConfig,
    load the desired MephistoDB and
    validate the config against the database contents, then
    return the database and validated config.

    Takes in an option to print out the configuration before returning
    """
    db = get_db_from_config(cfg)
    valid_config = augment_config_from_db(cfg, db)
    if print_config:
        print(OmegaConf.to_yaml(valid_config))
    return db, valid_config


def process_config_and_get_operator(
    cfg: DictConfig, print_config=False
) -> Tuple["Operator", DictConfig]:
    """
    Using a Hydra DictConfig built from a TaskConfig,
    return an operator for that task as well as a validated config.

    Takes in an option to print out the configuration before returning
    """
    db, valid_config = load_db_and_process_config(cfg, print_config=print_config)
    return Operator(db), valid_config


TaskFunction = TypeVar("TaskFunction", bound=Callable[..., Any])


def task_script(
    config: Optional[Type[TaskConfig]] = None,
    default_config_file: Optional[str] = None,
    config_path: str = "hydra_configs",  # Override if using a different dir
) -> Callable[[TaskFunction], Any]:
    """
    Create a decorator for the main of a Mephisto task script

    Must provide one of config (a TaskConfig dataclass) or default_config_file
    (the location of a default task config hydra yaml), the former
    will be preferred.

    May specify a config_path override if not using `hydra_configs` at the
    run script location.
    """
    if config is not None:
        used_config = config
    else:
        assert (
            default_config_file is not None
        ), "Must provide one of config or default_config_file"
        used_config = build_default_task_config(default_config_file)
    register_script_config(name="taskconfig", module=used_config)

    def task_script_wrapper(script_func: TaskFunction) -> TaskFunction:
        @functools.wraps(script_func)
        def process_config_and_run_main(cfg: "DictConfig"):
            operator, cfg = process_config_and_get_operator(cfg)
            try:
                ret_val = script_func(operator, cfg)
            except Exception as e:
                raise e
            finally:
                if not operator.is_shutdown:
                    operator.shutdown()
            return ret_val

        absolute_config_path = os.path.abspath(
            os.path.join(get_run_file_dir(), config_path)
        )
        hydra_wrapper = hydra.main(
            config_path=absolute_config_path,
            config_name="taskconfig",
            version_base="1.1",
        )
        return cast(TaskFunction, hydra_wrapper(process_config_and_run_main))

    return task_script_wrapper


def get_db_from_config(cfg: DictConfig) -> "MephistoDB":
    """
    Get a MephistoDB from the given configuration. As of now
    this defaults to a LocalMephistoDB
    """
    datapath = cfg.mephisto.get("datapath", None)

    if datapath is None:
        datapath = get_root_data_dir()

    database_path = os.path.join(datapath, "database.db")

    database_type = cfg.mephisto.database._database_type

    if database_type == "local":
        return LocalMephistoDB(database_path=database_path)
    elif database_type == "singleton":
        return MephistoSingletonDB(database_path=database_path)
    else:
        raise AssertionError(f"Provided database_type {database_type} is not valid")


def augment_config_from_db(script_cfg: DictConfig, db: "MephistoDB") -> DictConfig:
    """
    Check the database for validity of the incoming MephistoConfig, ensure
    that the config has all the necessary fields set.
    """
    cfg = script_cfg.mephisto
    requester_name = cfg.provider.get("requester_name", None)
    provider_type = cfg.provider.get("_provider_type", None)
    architect_type = cfg.architect.get("_architect_type", None)

    if requester_name is None:
        if provider_type is None:
            print("No requester specified, defaulting to mock")
            provider_type = "mock"
        if provider_type == "mock":
            req = get_mock_requester(db)
            requester_name = req.requester_name
        else:
            reqs = db.find_requesters(provider_type=provider_type)
            if len(reqs) == 0:
                print(
                    f"No requesters found for provider type {provider_type}, please "
                    f"register one. You can register with `mephisto register {provider_type}`, "
                    f"or `python mephisto/client/cli.py register {provider_type}` if you haven't "
                    "installed Mephisto using poetry."
                )
                exit(1)
            elif len(reqs) == 1:
                req = reqs[0]
                requester_name = req.requester_name
                print(
                    f"Found one `{provider_type}` requester to launch with: {requester_name}"
                )
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
            exit(1)
        requester_provider_type = reqs[0].provider_type
        if provider_type != requester_provider_type:
            print(
                f"{format_loud('[WARNING]:')} Mismatch between specified provider_type "
                f"{provider_type} and the provider_type of the specified requester "
                f"{requester_name}. Overriding with {requester_name}'s provider_type "
                f"{requester_provider_type}."
            )
        provider_type = requester_provider_type

    if provider_type in ["mturk"]:
        try_prerun_cleanup(db, cfg.provider.requester_name)
        input(
            f"This task is going to launch live on {provider_type}, press enter to continue: "
        )
    if provider_type in ["mturk_sandbox", "mturk"] and architect_type not in [
        "heroku",
        "ec2",
    ]:
        input(
            f"This task is going to launch live on {provider_type}, but your "
            f"provided architect is {architect_type}, are you sure you "
            "want to do this? : "
        )

    cfg.provider.requester_name = requester_name
    cfg.provider._provider_type = provider_type
    return script_cfg


def build_custom_bundle(
    custom_src_dir,
    force_rebuild: Optional[bool] = None,
    post_install_script: Optional[str] = None,
):
    """Locate all of the custom files used for a custom build, create
    a prebuild directory containing all of them, then build the
    custom source.

    Check dates to only go through this build process when files have changes
    """

    """
    If doing local package development make sure to check out the below link:
    https://github.com/facebookresearch/Mephisto/issues/811
    """

    IGNORE_FOLDERS = {"node_modules", "build"}

    prebuild_path = os.path.join(custom_src_dir, "webapp")

    IGNORE_FOLDERS = {os.path.join(prebuild_path, f) for f in IGNORE_FOLDERS}
    build_path = os.path.join(prebuild_path, "build", "bundle.js")

    # see if we need to rebuild
    if force_rebuild is None or force_rebuild == False:
        if os.path.exists(build_path):
            created_date = os.path.getmtime(build_path)
            up_to_date = True

            for root, dirs, files in os.walk(prebuild_path):
                for igf in IGNORE_FOLDERS:
                    should_ignore = False
                    if igf in root:
                        should_ignore = True
                if should_ignore:
                    continue
                if not up_to_date:
                    break
                for fname in files:
                    path = os.path.join(root, fname)
                    if os.path.getmtime(path) > created_date:
                        up_to_date = False
                        break
            if up_to_date:
                return build_path

    # navigate and build
    return_dir = os.getcwd()
    os.chdir(prebuild_path)

    packages_installed = subprocess.call(["npm", "install"])
    if packages_installed != 0:
        raise Exception(
            "please make sure npm is installed, otherwise view "
            "the above error for more info."
        )

    if post_install_script is not None and len(post_install_script) > 0:
        did_fail_script = subprocess.call(["bash", post_install_script])
        if did_fail_script != 0:
            raise Exception(
                "Please make sure that the post_install_script mentioned in your hydra config "
                "exists in the webapp folder for this task!\n"
                "The script should be able to be ran with bash"
            )

    webpack_complete = subprocess.call(["npm", "run", "dev"])
    if webpack_complete != 0:
        raise Exception(
            "Webpack appears to have failed to build your "
            "frontend. See the above error for more information."
        )

    # cleanup and return
    os.chdir(return_dir)
    return build_path


def print_out_task_names(header: str, task_names: List[str]) -> None:
    """Prints out task names and formats them nicely using rich"""
    if len(task_names) == 0:
        print(
            "\n[red]There are no task names found[/red] \nYou should launch a task first and then run this script after the task is shut down\n"
        )
        quit()
    task_names_text = """# {header} \n ## Task Names:""".format(header=header)
    for task_name in task_names:
        task_names_text += "\n* " + task_name

    task_names_markdown = Markdown(task_names_text)
    console.print(task_names_markdown)
    print("")
