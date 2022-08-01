from mdutils.mdutils import MdUtils
from mephisto.client.cli_commands import get_wut_arguments
from mephisto.operations.registry import (
    get_valid_provider_types,
)
from mephisto.scripts.local_db.gh_actions.auto_generate_blueprint import (
    create_blueprint_info,
)


def main():
    requester_file = MdUtils(
        file_name="../../../../docs/web/docs/reference/requesters.md",
    )
    requester_file.new_header(level=1, title="Requesters")
    requester_file.new_paragraph(
        "Requesters are Mephisto's wrapper around an identity for a CrowdProvider, usually storing the credentials for an account to launch tasks from."
    )
    requester_file.new_paragraph(
        "Use `mephisto requesters` to see registered requesters, and `mephisto register <requester type>` to register."
    )
    valid_requester_types = get_valid_provider_types()
    for requester_type in valid_requester_types:
        requester_file.new_header(level=2, title=requester_type.replace("_", " "))
        args = get_wut_arguments(
            ("requester={requester_name}".format(requester_name=requester_type),)
        )
        arg_dict = args[0]
        create_blueprint_info(requester_file, arg_dict)

    requester_file.create_md_file()


if __name__ == "__main__":
    main()
