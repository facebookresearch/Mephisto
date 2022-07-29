from mephisto.client.cli_commands import get_wut_arguments
from mephisto.utils.rich import console
from mdutils.mdutils import MdUtils


def main():
    blueprint_file = MdUtils(
        file_name="../../../../docs/web/docs/reference/Blueprints.md",
    )
    blueprint_file.new_header(level=1, title="Blueprints")
    blueprint_file.new_header(level=2, title="Static React Task")

    blueprint_file.new_header(level=2, title="Static Task")

    blueprint_file.new_header(level=2, title="Remote Procedure")

    blueprint_file.new_header(level=2, title="Parlai Chat")

    blueprint_file.new_header(level=2, title="Mock")

    blueprint_file.create_md_file()

    names = ["static_react_task"]
    args = get_wut_arguments(("blueprint=static_react_task",))
    args_dict = args[0]


# ('blueprint=static_react_task',)

if __name__ == "__main__":
    main()
