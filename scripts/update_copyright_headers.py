#!/usr/bin/env python3

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Script to insert legal header to files across the repo
"""

import glob
import os
import traceback

from typing import List
from typing import Optional

REPO_ROOT_PATH = "../"

EXCLUDE_DIR_NAMES = [
    "data",
    "build",
    "node_modules",
    "__pycache__",
]

COPYRIGHT_LINES = [
    "Copyright (c) Meta Platforms and its affiliates.",
    "This source code is licensed under the MIT license found in the",
    "LICENSE file in the root directory of this source tree.",
]


class ProcessingError(Exception):
    pass


class UnsupportedFile(Exception):
    pass


def _add_prefix_suffix(prefix: str, lines: List[str], suffix: Optional[str] = None) -> List[str]:
    lines = lines[:]
    for i, line in enumerate(lines):
        lines[i] = (prefix or "") + line + (suffix or "")
    return lines


def _make_copyright_lines(ext: str) -> List[str]:
    """
    Insert copyright as comment lines specific to file extension
    """
    lines = []

    ext = ext.lstrip(".")
    if ext in ["py", "sh", "yml", "yaml"]:
        lines = _add_prefix_suffix("# ", COPYRIGHT_LINES)
    elif ext in ["js", "jsx", "ts", "tsx", "css", "scss"]:
        lines = ["/*"] + _add_prefix_suffix(" * ", COPYRIGHT_LINES) + [" */"]
    elif ext in ["md", "html"]:
        lines = ["<!---"] + _add_prefix_suffix("  ", COPYRIGHT_LINES) + ["-->"]
    else:
        raise UnsupportedFile(f"Unsupported file extension `{ext}`")

    return _add_prefix_suffix(None, lines, "\n")


def _update_copyright_header(file_path: str, replace_existing: bool = False):
    """
    Add or replace copyright notice at the top of a file
    """
    ext = os.path.splitext(file_path)[1].lower()

    EXAMINED_LINES = 10

    with open(file_path, "r") as f:
        lines = f.readlines()

    if len(lines) < 2:
        raise UnsupportedFile("File has fewer than one line")

    # Check copyright presence at the top of the file
    anchor_line_number = -2
    for i, line in enumerate(lines[:EXAMINED_LINES]):
        text = line[:50].lower()
        if "copyright" in text:
            anchor_line_number = -1
        if anchor_line_number == -1 and ("meta" in text or "facebook" in text):
            anchor_line_number = i

    new_lines = None
    if anchor_line_number < 0:
        # Insert a new copyright notice
        print("Inserting new notice")

        if lines[0].startswith("#!") and not lines[1].startswith("#!"):
            # Skipping shebang line
            insert_at_line_number = 1
        else:
            # Insert at the top of the file
            insert_at_line_number = 0

        new_lines = (
            lines[:insert_at_line_number]
            + (["\n"] if insert_at_line_number > 0 else [])
            + _make_copyright_lines(ext)
            + ["\n"]
            + lines[insert_at_line_number:]
        )
    elif replace_existing:
        # Replace existing copyright notice
        print("Updating existing notice")

        first_line_number = 0
        last_line_number = None
        for i, line in enumerate(lines[:EXAMINED_LINES]):
            if line == "\n":
                # Empty line
                if i < anchor_line_number:
                    first_line_number = i + 1
                else:
                    last_line_number = i - 1
                    break

        if last_line_number is None:
            raise ProcessingError(
                "Could not find the end of existing copyright notice "
                "(empty line missing right after?)"
            )

        # Prevent removing code lines that are "glued" to the bottom of a copyright notice
        had_empty_line_after_comment = True
        is_comment_last_line = lambda line: bool(set(["/", "#", ">", "*"]) & set(line[:5]))
        while last_line_number and not is_comment_last_line(lines[last_line_number]):
            last_line_number -= 1
            had_empty_line_after_comment = False

        if last_line_number < anchor_line_number:
            raise ProcessingError("Could not confirm last line of copyright note comment")

        # Note that we're also replacing an empty line after copyright notice
        lines_before_copyright = lines[:first_line_number]
        lines_after_copyright = lines[last_line_number + 1 + had_empty_line_after_comment :]
        new_lines = (
            lines_before_copyright + _make_copyright_lines(ext) + ["\n"] + lines_after_copyright
        )

    if new_lines:
        with open(file_path, "w") as f:
            f.writelines(new_lines)


def run(
    start_path: str,
    extension: Optional[str] = None,
    replace_existing: Optional[bool] = False,
):
    """
    :param start_path: Directory in which we will recursively process files
    :param extension: When specified, we"ll only process files with this extension
    :param replace_existing: When True, we will replace existing copyright notice if found
    """
    assert "" not in COPYRIGHT_LINES, "Copyright notice must not contain empty lines"

    # Filter files with glob
    glob_pattern = start_path.rstrip("/") + "/**"
    if extension:
        glob_pattern += "/*." + extension.lstrip(".")
    all_paths = glob.glob(glob_pattern, recursive=True)

    # Apply filters that `glob` filter doesn"t support
    valid_file_paths = [
        path
        for path in all_paths
        if os.path.isfile(path) and all(f"/{ex_dir}/" not in path for ex_dir in EXCLUDE_DIR_NAMES)
    ]
    print(f"Processing {len(valid_file_paths)} files")

    # Apply copyright header to each file
    n_files = len(valid_file_paths)
    updated = []
    skipped = []
    failed = []
    for i, path in enumerate(valid_file_paths):
        print(f"[{i+1}/{n_files}] Processing {path}...")

        try:
            _update_copyright_header(path, replace_existing)
            updated.append(path)
        except UnsupportedFile as e:
            print("Skipping:", e)
            skipped.append(path)
        except UnicodeDecodeError:
            print("Skipping binary file")
            skipped.append(path)
        except ProcessingError as e:
            print("Exception:", e, "\n")
            failed.append(path)
        except Exception:
            print(traceback.format_exc())
            failed.append(path)

    print(
        f"\nFinished processing. "
        f"Updated {len(updated)}, skipped {len(skipped)}, failed {len(failed)} files."
    )
    if failed:
        failed_files = "\n\t" + "\n\t".join(failed)
        print(f"\nThe following files failed: {failed_files}")


if __name__ == "__main__":
    run(
        REPO_ROOT_PATH,
        replace_existing=True,
    )
