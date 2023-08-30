import typer

from .commands.cipher import app as cipher

app = typer.Typer()
app.add_typer(cipher, name="cipher")


@app.callback()
def callback():
    """
    Quest utils CLI app.
    """
