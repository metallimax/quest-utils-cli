import typer

from functools import reduce
from random import choices
from rich.console import Console
from rich.theme import Theme
from typing import Annotated, Dict, Optional, Tuple

from ....common import ALPHABET
from ....config import settings


app = typer.Typer()

custom_theme = Theme({"key": "yellow", "value": "cyan"})
console = Console(theme=custom_theme)
err_console = Console(stderr=True)


class Enigma(object):
    def __init__(
        self,
        plugin_board: str,
        rotors: Tuple[int, int, int],
        positions: Tuple[int, int, int],
    ):
        self.steps = []
        self.rotors = rotors
        self.positions = positions
        self.plugin_board = self._get_mapping(plugin_board, bidirectional=True)
        self.rf = self._get_mapping(settings.ENIGMA.REFLECTOR)

        r1_name = f"ROTOR{rotors[0]}"
        r2_name = f"ROTOR{rotors[1]}"
        r3_name = f"ROTOR{rotors[2]}"

        rotor1 = settings.ENIGMA[r1_name]
        rotor2 = settings.ENIGMA[r2_name]
        rotor3 = settings.ENIGMA[r3_name]

        self.r1 = rotor1.RING
        self.r2 = rotor2.RING
        self.r3 = rotor3.RING

        self._step(f"Rotor names: ({r1_name}, {r2_name}, {r3_name})")
        self._step(f"Rotor rings: ({self.r1}, {self.r2}, {self.r3})")

        self.m1 = self._get_mapping(rotor1.MAPPING)
        self.m2 = self._get_mapping(rotor2.MAPPING)
        self.m3 = self._get_mapping(rotor3.MAPPING)
        self._set_rotor_mapping()

    def _step(self, step):
        self.steps.append(step)

    def _inc_positions(self):
        p1, p2, p3 = self.positions

        if p2 == self.r2 and p3 == self.r3:
            p1 = (p1 + 1) % len(ALPHABET)
            self._step(f"Inc. pos. 1 to {p1} due to pos. 2 is {p2} and pos. 3 is {p3}")
        if p3 == self.r3:
            p2 = (p2 + 1) % len(ALPHABET)
            self._step(f"Inc. pos. 2 to {p2} due to pos. 3 equals {p3}")
        p3 = (p3 + 1) % len(ALPHABET)
        self._step(f"Inc. pos. 3 to {p3}")

        self.positions = (p1, p2, p3)
        self._set_rotor_mapping()

    def _set_rotor_mapping(self):
        p1, p2, p3 = self.positions

        self._step(f"Setting rot. mapping according to pos. ({p1}, {p2}, {p3})")

        # TODO check if this is correct
        self.pg_r3 = self._get_rotor_mapping(p3)
        self.r3_r2 = self._get_rotor_mapping(p2 - p3)
        self.r2_r1 = self._get_rotor_mapping(p2 - p1)
        self.r1_rf = self._get_rotor_mapping(p1)

    def _get_rotor_mapping(self, position):
        return {
            ALPHABET[i]: ALPHABET[(i + position) % 26] for i in range(len(ALPHABET))
        }

    def _get_mapping(self, str_mapping: str, bidirectional: bool = False):
        plugin_board_mapping = {}

        for part in str_mapping.split(";"):
            a, b = part.split(",")
            plugin_board_mapping[a] = b
            if bidirectional:
                plugin_board_mapping[b] = a

        return plugin_board_mapping

    def _apply(self, char: str, what: str, reverse: bool = False) -> str:
        d = getattr(self, what, {})
        if reverse:
            d = {v: k for k, v in d.items()}
        return d.get(char, char)

    def _cipher_char(self, char: str) -> str:
        if char not in ALPHABET:
            return char

        chars = [char]
        char = self._apply(char, "plugin_board")
        chars.append(char)
        char = self._apply(char, "pg_r3")
        chars.append(char)
        # char = self._apply(char, "r1")
        # char = self._apply(char, "r1_r2")
        # char = self._apply(char, "r2")
        # char = self._apply(char, "r2_r3")
        # char = self._apply(char, "r3")
        # char = self._apply(char, "r3_rf")
        # char = self._apply(char, "rf")
        # char = self._apply(char, "r3_rf", reverse=True)
        # char = self._apply(char, "r3", reverse=True)
        # char = self._apply(char, "r2_r3", reverse=True)
        # char = self._apply(char, "r2", reverse=True)
        # char = self._apply(char, "r1_r2", reverse=True)
        # char = self._apply(char, "r1", reverse=True)
        # char = self._apply(char, "pg_r1", reverse=True)
        # char = self._apply(char, "plugin_board")

        self._step(f"{' -> '.join(chars)}")
        self._inc_positions()

        return char

    def _decipher_char(self, char: str) -> str:
        if char not in ALPHABET:
            return char

        # TODO check the order here

        return char

    def cipher(self, text: str) -> str:
        res = ""

        for c in text.lower():
            res += self._cipher_char(c)

        return res

    def decipher(self, text: str) -> str:
        res = ""

        for c in text.lower():
            res += self._cipher_char(c)

        return res


def _check_rotor(rotor: int):
    if rotor < 1 or rotor > 5:
        raise typer.BadParameter("Rotor value should be between 1 and 5 (included).")

    return rotor


def _check_position(rotor: int):
    if rotor < 1 or rotor > 26:
        raise typer.BadParameter(
            "Position value should be between 1 and 26 (included)."
        )

    return rotor


def _check_plugin_board(plugin_board: str):
    if plugin_board is None:
        return None

    trans_table = str.maketrans("", "", ";,")
    plugin_board_trans = plugin_board.translate(trans_table)
    occurrences = {
        k: reduce(lambda acc, c: acc + 1 if c == k else acc, plugin_board_trans, 0)
        for k in set(plugin_board_trans)
    }

    if any([o > 1 for o in occurrences.values()]):
        raise typer.BadParameter(
            "Plugin board should define only one mapping for each letter."
        )

    return plugin_board


@app.command()
def cipher(
    text: str,
    r1: Annotated[
        int,
        typer.Option("--rotor1", "-r1", help="Rotor 1", callback=_check_rotor),
    ],
    r2: Annotated[
        int,
        typer.Option("--rotor2", "-r2", help="Rotor 2", callback=_check_rotor),
    ],
    r3: Annotated[
        int,
        typer.Option("--rotor3", "-r3", help="Rotor 3", callback=_check_rotor),
    ],
    p1: Annotated[
        int,
        typer.Option("--position1", "-p1", help="Position 1", callback=_check_position),
    ],
    p2: Annotated[
        int,
        typer.Option("--position2", "-p2", help="Position 2", callback=_check_position),
    ],
    p3: Annotated[
        int,
        typer.Option("--position3", "-p3", help="Position 3", callback=_check_position),
    ],
    plugin_board: Annotated[
        Optional[str],
        typer.Option(
            ...,
            "--plugin-board",
            "-p",
            help="Plugin board",
            callback=_check_plugin_board,
        ),
    ] = settings.ENIGMA.PLUGIN_BOARD,
):
    """
    Cipher action.
    """

    enigma = Enigma(
        plugin_board=plugin_board,
        positions=(p1, p2, p3),
        rotors=(r1, r2, r3),
    )
    res = enigma.cipher(text)

    console.print("\n".join(enigma.steps))
    console.print("\n")
    console.print(res)


# @app.command()
# def decipher(
#     text: str,
#     rotor1: Annotated[
#         int,
#         typer.Option("--rotor-1", "-r1", help="Rotor 1", callback=_check_rotor),
#     ],
#     rotor2: Annotated[
#         int,
#         typer.Option("--rotor-2", "-r2", help="Rotor 2", callback=_check_rotor),
#     ],
#     rotor3: Annotated[
#         int,
#         typer.Option("--rotor-3", "-r3", help="Rotor 3", callback=_check_rotor),
#     ],
#     plugin_board: Annotated[
#         Optional[str],
#         typer.Option(
#             "--plugin-board",
#             "-p",
#             help="Plugin board",
#             callback=_check_plugin_board,
#         ),
#     ] = settings.ENIGMA.PLUGIN_BOARD,
# ):
#     """
#     Decipher action.
#     """

#     enigma = Enigma(plugin_board=plugin_board, rotor_positions=(rotor1, rotor2, rotor3))
#     res = enigma.decipher(text)

#     console.print(res)


@app.command()
def gen_rotor():
    scrambled = choices(ALPHABET, k=len(ALPHABET))
    rotor = []

    for i in range(len(ALPHABET)):
        rotor.append(f"{ALPHABET[i]},{scrambled[i]}")

    console.print(";".join(rotor))


@app.callback()
def callback():
    """
    Enigma Cipher commands.
    """


if __name__ == "__main__":
    app()
