from typing import List
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()


def create_table(headers: List[str], title: str) -> Table:
    return Table(*headers, title=title, box=box.ROUNDED, expand=True, show_lines=True)
