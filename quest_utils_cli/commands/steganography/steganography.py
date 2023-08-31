from __future__ import absolute_import, unicode_literals

import typer

from pathlib import Path
from rich.console import Console
from rich.theme import Theme
from typing import Annotated


app = typer.Typer()

custom_theme = Theme({"key": "yellow", "value": "cyan"})
console = Console(theme=custom_theme)
err_console = Console(stderr=True)


@app.command()
def encode(
    content: str,
    input: Annotated[Path, typer.Option(..., "--input", "-i", help="Input image file path")],
    output: Annotated[Path, typer.Option(..., "--output", "-o", help="Output image file path")],
):
    # Steganography.encode(input, output, content)
    raise NotImplementedError("I beg you to implement me!")


@app.command()
def decode(
    input: Annotated[Path, typer.Option(..., "--input", "-i", help="Input image file path")],
):
    # content = Steganography.decode(input)
    # console.log(content)
    raise NotImplementedError("I beg you to implement me!")


@app.callback()
def callback():
    """
    Steganography commands.
    """


if __name__ == "__main__":
    app()
