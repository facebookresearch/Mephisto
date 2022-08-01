from mdutils.mdutils import MdUtils
from mephisto.client.cli_commands import get_wut_arguments
from mephisto.operations.registry import (
    get_valid_provider_types,
)
from mephisto.scripts.local_db.gh_actions.auto_generate_blueprint import (
    create_blueprint_info,
)


def main():
    provider_file = MdUtils(
        file_name="../../../../docs/web/docs/reference/providers.md",
    )
    provider_file.new_header(level=1, title="Providers")
    provider_file.new_paragraph(
        "Crowd providers standardize access to external crowd workers, by wrapping external API communication through a standardized interface."
    )
    valid_provider_types = get_valid_provider_types()
    for provider_type in valid_provider_types:
        provider_file.new_header(level=2, title=provider_type.replace("_", " "))
        args = get_wut_arguments(
            ("provider={provider_name}".format(provider_name=provider_type),)
        )
        arg_dict = args[0]
        create_blueprint_info(provider_file, arg_dict)

    provider_file.create_md_file()


if __name__ == "__main__":
    main()
