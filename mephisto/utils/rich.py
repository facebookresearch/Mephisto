# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List
from rich.console import Console
from rich.table import Table
from rich import box
from rich.markdown import Markdown

console = Console()


def create_table(headers: List[str], title: str) -> Table:
    return Table(*headers, title=title, box=box.ROUNDED, expand=True, show_lines=True)


def print_out_valid_options(markdown_text: str, valid_options: List[str]) -> None:
    for valid_option in valid_options:
        markdown_text += "\n* " + valid_option
    console.print(Markdown(markdown_text))
    console.print("")
