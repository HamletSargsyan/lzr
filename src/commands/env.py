import typer
from core import Lzr
from helpers.utils import extract_version
from settings import VERSION_FILE_NAME

app = typer.Typer()


@app.command("global")
def set_global_version(version: str):
    typer.echo(f"Установка глобальной версии Lazurite: {version}")
    lzr = Lzr()
    lzr.config.set("lazurite", "version", extract_version(version))
    typer.echo(f"Глобальная версия Lazurite установлена: {version}")


@app.command("local")
def set_local_version(version: str):
    typer.echo(f"Установка локальной версии Lazurite: {version}")

    with open(VERSION_FILE_NAME, "w") as f:
        f.write(version)

    typer.echo(f"Локальная версия Lazurite установлена: {version}")


@app.command("version")
def show_version():
    lzr = Lzr()
    version = lzr.get_lazurite_version()
    typer.echo(f"Текущая версия Lazurite: {version}")
