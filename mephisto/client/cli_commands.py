from mephisto.utils.rich import console, print_out_valid_options, create_table
import rich_click as click  # type: ignore
from rich import print


def get_wut_arguments(args):
    """Display information about hydra config properties"""
    from mephisto.operations.registry import (
        get_blueprint_from_type,
        get_crowd_provider_from_type,
        get_architect_from_type,
        get_valid_blueprint_types,
        get_valid_provider_types,
        get_valid_architect_types,
    )

    if len(args) == 0:
        print(
            "\n[red]Usage: mephisto wut <abstraction>[=<type>] [...specific args to check][/red]"
        )
        abstractions_table = create_table(
            ["Abstraction", "Description"], "\n\n[b]Abstractions[/b]"
        )
        abstractions_table.add_row(
            "blueprint",
            f"The blueprint determines the task content. \nValid blueprints types are [b]{get_valid_blueprint_types()}[/b]",
        )
        abstractions_table.add_row(
            "architect",
            f"The architect determines the server where a task is hosted. \nValid architects types are [b]{get_valid_architect_types()}[/b]",
        )
        abstractions_table.add_row(
            "requester",
            f"The requester is an account for a crowd provider. \nValid requester types types are [b]{get_valid_provider_types()}[/b]. \n"
            "\nUse `mephisto requesters` to see registered requesters, and `mephisto register <requester type>` to register.",
        )
        abstractions_table.add_row(
            "provider",
            f"The crowd provider determines the source of the crowd workers. \nValid provider types are [b]{get_valid_provider_types()}[/b]",
        )
        console.print(abstractions_table)
        return

    VALID_ABSTRACTIONS = ["blueprint", "architect", "requester", "provider", "task"]

    from mephisto.operations.hydra_config import (
        get_extra_argument_dicts,
        get_task_state_dicts,
    )

    VALID_ABSTRACTIONS = ["blueprint", "architect", "requester", "provider", "task"]

    abstraction_equal_split = args[0].split("=", 1)
    abstraction = abstraction_equal_split[0]

    if abstraction not in VALID_ABSTRACTIONS:
        print(
            f"[red]Given abstraction {abstraction} not in valid abstractions {VALID_ABSTRACTIONS}][/red]"
        )
        return

    if abstraction == "task":
        from mephisto.data_model.task_run import TaskRun

        target_class = TaskRun
    else:
        if len(abstraction_equal_split) == 1:
            # querying about the general abstraction
            if abstraction == "blueprint":
                click.echo("The blueprint determines the task content.\n")
                valid_blueprints_text = """**Valid blueprints are:**"""
                print_out_valid_options(
                    valid_blueprints_text, get_valid_blueprint_types()
                )
                return
            elif abstraction == "architect":
                click.echo(
                    "The architect determines the server where a task is hosted.\n"
                )
                valid_architect_text = """**Valid architects are:**"""
                print_out_valid_options(
                    valid_architect_text, get_valid_architect_types()
                )
                return
            elif abstraction == "requester":
                click.echo(
                    f"The requester is an account for a crowd provider. \n"
                    "Use `mephisto requesters` to see registered requesters, and `mephisto register <requester type>` to register.\n"
                )
                valid_requester_text = """**Valid requesters are:**"""
                print_out_valid_options(
                    valid_requester_text, get_valid_provider_types()
                )
                return
            elif abstraction == "provider":
                click.echo(
                    "The crowd provider determines the source of the crowd workers.\n"
                )
                valid_provider_text = """**Valid providers are:**"""
                print_out_valid_options(valid_provider_text, get_valid_provider_types())
                return

        # There's a specific abstraction to check
        abstract_value = abstraction_equal_split[1]
        target_class = None
        valid = None
        if abstraction == "blueprint":
            try:
                target_class = get_blueprint_from_type(abstract_value)
            except:
                valid = get_valid_blueprint_types()
        elif abstraction == "architect":
            try:
                target_class = get_architect_from_type(abstract_value)
            except:
                valid = get_valid_architect_types()
        elif abstraction == "provider":
            try:
                target_class = get_crowd_provider_from_type(abstract_value)
            except:
                valid = get_valid_provider_types()
        elif abstraction == "requester":
            try:
                target_class = get_crowd_provider_from_type(
                    abstract_value
                ).RequesterClass
            except:
                valid = get_valid_provider_types()
        if valid is not None:
            print(f"\n[b]The valid types for {abstraction} are:[/b]")
            valid_options_text = """"""
            print_out_valid_options(valid_options_text, valid)
            print(f"[red]'{abstract_value}' not found[/red]\n")
            return

    arg_dict = get_extra_argument_dicts(target_class)[0]
    click.echo(arg_dict["desc"])
    checking_args = arg_dict["args"]
    if len(args) > 1:
        checking_args = {k: v for k, v in checking_args.items() if k in args[1:]}
    checking_args_keys = list(checking_args.keys())
    if len(checking_args_keys) > 0:
        first_arg = checking_args_keys[0]
        first_arg_keys = list(checking_args[first_arg].keys())
        args_table = create_table(
            first_arg_keys,
            "\n[b]{abstraction} Arguments[/b]".format(
                abstraction=abstraction.capitalize()
            ),
        )
        for arg in checking_args:
            arg_keys = checking_args[arg].keys()
            if "required" in arg_keys and checking_args[arg]["required"] == True:
                checking_args[arg]["required"] = "[b]{requiredVal}[/b]".format(
                    requiredVal=checking_args[arg]["required"]
                )
            if arg == "tips_location":
                checking_args[arg]["default"] = "path_to_task/assets/tips.csv"
            arg_values = list(checking_args[arg].values())
            arg_values = [str(x) for x in arg_values]

            args_table.add_row(*arg_values)
        console.print(args_table)
        if abstraction != "blueprint":
            return [arg_dict]
    if abstraction == "blueprint":
        state_args = get_task_state_dicts(target_class)[0]["args"]
        if len(args) > 1:
            state_args = {k: v for k, v in state_args.items() if k in args[1:]}
        state_args_keys = list(state_args.keys())
        if len(state_args_keys) > 0:
            click.echo(
                f"\n\nAdditional SharedTaskState args from {target_class.SharedStateClass.__name__}, which may be configured in your run script"
            )
            first_state_arg = state_args_keys[0]
            first_arg_keys = list(state_args[first_state_arg].keys())

            state_args_table = create_table(
                first_arg_keys, "\n[b]Additional Shared TaskState args[/b]"
            )

            for arg in state_args:
                arg_values = list(state_args[arg].values())
                arg_values = [str(x) for x in arg_values]
                state_args_table.add_row(*arg_values)
            console.print(state_args_table)
            return [arg_dict, state_args]
