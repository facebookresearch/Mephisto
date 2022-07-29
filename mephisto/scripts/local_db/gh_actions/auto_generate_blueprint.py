from mephisto.client.cli_commands import get_wut_arguments
from mdutils.mdutils import MdUtils
from copy import deepcopy


def create_blueprint_info(blueprint_file, arg_dict):
    blueprint_file.new_paragraph(arg_dict["desc"].strip())
    arg_keys = list(arg_dict["args"].keys())
    first_arg = list(arg_dict["args"].keys())[0]
    first_arg_keys = list(arg_dict["args"][first_arg].keys())

    list_of_strings = deepcopy(first_arg_keys)

    for cur_key in arg_keys:
        extension_list = []
        for first_arg_key in first_arg_keys:
            item_content = arg_dict["args"][cur_key][first_arg_key]
            item_to_append = (
                "".join(item_content.splitlines())
                if isinstance(item_content, str)
                else item_content
            )
            extension_list.append(item_to_append)
        list_of_strings.extend(extension_list)

    blueprint_file.new_line()

    # Add 1 to rows to account for header row
    blueprint_file.new_table(
        rows=len(arg_keys) + 1,
        columns=len(first_arg_keys),
        text=list_of_strings,
        text_align="left",
    )


def main():
    blueprint_file = MdUtils(
        file_name="../../../../docs/web/docs/reference/Blueprints.md",
    )
    blueprint_file.new_header(level=1, title="Blueprints")

    blueprint_file.new_header(level=2, title="Static React Task")
    args = get_wut_arguments(("blueprint=static_react_task",))
    arg_dict = args[0]
    create_blueprint_info(blueprint_file, arg_dict)

    blueprint_file.new_header(level=2, title="Static Task")
    args = get_wut_arguments(("blueprint=static_task",))
    arg_dict = args[0]
    create_blueprint_info(blueprint_file, arg_dict)
    blueprint_file.new_header(level=2, title="Remote Procedure")

    args = get_wut_arguments(("blueprint=remote_procedure",))
    arg_dict = args[0]
    create_blueprint_info(blueprint_file, arg_dict)

    blueprint_file.new_header(level=2, title="Parlai Chat")

    args = get_wut_arguments(("blueprint=parlai_chat",))
    arg_dict = args[0]
    create_blueprint_info(blueprint_file, arg_dict)

    blueprint_file.new_header(level=2, title="Mock")

    args = get_wut_arguments(("blueprint=mock",))
    arg_dict = args[0]
    create_blueprint_info(blueprint_file, arg_dict)
    blueprint_file.create_md_file()


if __name__ == "__main__":
    main()
