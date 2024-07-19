import os
import typer

from helpers.venv import Venv
from settings import ENV_LAZURITE_VENV_PATH, VENV_NAME

app = typer.Typer()


@app.command("create")
def create_env():
    typer.echo("Creating environment")
    venv = Venv()

    if venv.path.exists():
        raise NotImplementedError  # TODO

    venv.create()


@app.command("activate")
def activate_env(path: str = f"./{VENV_NAME}"):
    typer.echo("Activating environment")

    os.environ[ENV_LAZURITE_VENV_PATH] = path


@app.command("deactivate")
def deactivate_env():
    typer.echo("Deactivating environment")
    del os.environ[ENV_LAZURITE_VENV_PATH]
