import typer


from .pigpen import app as pigpen
from .enigma import app as enigma


app = typer.Typer()

app.add_typer(pigpen, name="pigpen")
app.add_typer(enigma, name="enigma")


@app.callback()
def callback():
    """
    Cipher commands.
    """


if __name__ == "__main__":
    app()
