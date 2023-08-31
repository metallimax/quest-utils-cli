import typer

from .commands.cipher import app as cipher
from .commands.steganography import app as steganography

app = typer.Typer()
app.add_typer(cipher, name="cipher")
app.add_typer(steganography, name="steg")


@app.callback()
def callback():
    """
    Quest utils CLI app.
    """
