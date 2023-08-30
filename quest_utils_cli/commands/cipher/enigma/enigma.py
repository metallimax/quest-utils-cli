import typer

from rich.console import Console
from rich.theme import Theme


app = typer.Typer()

custom_theme = Theme({"key": "yellow", "value": "cyan"})
console = Console(theme=custom_theme)
err_console = Console(stderr=True)

@app.command()
def cipher():
    """
    Cipher action.
    """

    console.print("Enigma cipher")

@app.command()
def decipher():
    """
    Decipher action.
    """

    console.print("Enigma decipher")


@app.callback()
def callback():
    """
    Enigma Cipher commands.
    """


if __name__ == "__main__":
    app()
