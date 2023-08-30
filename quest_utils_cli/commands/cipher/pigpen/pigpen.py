import string
import typer

from importlib import resources as impresources
from pathlib import Path
from PIL import Image
from rich.console import Console
from rich.theme import Theme
from typing_extensions import Annotated

# from ....assets.cipher import pigpen


app = typer.Typer()

custom_theme = Theme({"key": "yellow", "value": "cyan"})
console = Console(theme=custom_theme)
err_console = Console(stderr=True)

ALPHABET = string.ascii_lowercase
ALPHABET_SET = set(ALPHABET)
ALPHABET_SET_W_SPACE = ALPHABET_SET | {" "}


class Pigpen:
    def __init__(self, password: str):
        self.password = password.lower()
        self.table = self._get_reodered_alphabet()

    def _get_reodered_alphabet(self):
        pwd_set = set(self.password) & ALPHABET_SET
        pwd_prefix = []
        for c in self.password:
            if c in pwd_set and c not in pwd_prefix:
                pwd_prefix.append(c)
        alphabet_suffix = [c for c in ALPHABET if c in ALPHABET_SET - pwd_set]
        reordered_alphabet = [" "] + pwd_prefix + alphabet_suffix

        return reordered_alphabet

    def cipher(self, text: str):
        text = [c for c in text.lower() if c in ALPHABET_SET_W_SPACE]
        res = [self.table.index(c) for c in text]

        return res

    def decipher(self, text: str):
        Exception(f"Can't decipher Pigpen yet! Sorry '{text}'")


@app.command()
def cipher(
    text: str,
    password: Annotated[
        str, typer.Option(prompt=True, confirmation_prompt=True, hide_input=True)
    ],
    output: Annotated[Path, typer.Option(..., "--output", "-o")],
):
    """
    Cipher action.
    """

    pigpen = Pigpen(password=password)
    ciphered = pigpen.cipher(text)

    ciphered_charset = set(ciphered)
    sprites_root = impresources.files("quest_utils_cli.assets.cipher.pigpen")
    imgs = {k: Image.open(sprites_root / f"{k:02d}.png") for k in ciphered_charset}

    width = sum([imgs[k].width for k in ciphered])
    height = max([imgs[k].height for k in ciphered])
    dst_img = Image.new("RGB", (width, height))
    origin = 0
    for k in ciphered:
        img = imgs[k]
        dst_img.paste(img, (origin, 0))
        origin += img.width

    dst_img.save(output)


@app.command()
def decipher(
    text: str,
    password: Annotated[
        str, typer.Option(prompt=True, confirmation_prompt=True, hide_input=True)
    ],
):
    """
    Decipher action.
    """

    pigpen = Pigpen(password=password)
    res = pigpen.decipher(text)
    console.print(res)


@app.callback()
def callback():
    """
    Pigpen Cipher commands.
    """


if __name__ == "__main__":
    app()
