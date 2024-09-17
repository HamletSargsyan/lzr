import shutil
from typing import Annotated
import typer
import requests
from rich.progress import Progress

from api import LazuriteGithubApi
from core import Lzr
from settings import console
from helpers.utils import (
    extract_version,
    get_release_by_version,
    get_release_versions,
    get_version_from_release,
    lazurite_run,
)

app = typer.Typer()


@app.command("install")
def install_lazurite(version: Annotated[str, typer.Argument()] = "latest"):
    lzr = Lzr()

    with Progress(console=console) as progress:
        task_fetching = progress.add_task("Fetching GitHub", total=100)
        progress.console.log(f"Установка Lazurite версии: {version}")

        try:
            release = get_release_by_version(version)
            release.raise_for_status()
            release_data = release.json()
            progress.update(task_fetching, advance=100)


            version = get_version_from_release(release_data)
            jar_url = next(
                (
                    asset["browser_download_url"]
                    for asset in release_data.get("assets", [])
                    if asset["name"].endswith(".jar")
                ),
                None,
            )

            if not jar_url:
                typer.echo("JAR файл не найден в релизе.")
                return

            path = lzr.path / "lazurite" / version
            path.mkdir(parents=True, exist_ok=True)
            jar_path = path / "lazurite.jar"

            response = requests.get(jar_url, stream=True)
            total_length = int(response.headers.get("content-length", 0))

            if response.status_code == 200:
                with open(jar_path, "wb") as file:
                    download_task = progress.add_task("Скачивание", total=total_length)
                    for chunk in response.iter_content(chunk_size=4096):
                        file.write(chunk)
                        progress.update(download_task, advance=len(chunk))
                progress.log("Lazurite JAR успешно скачан.")

                if not lzr.get_all_versions():
                    lzr.config.set("lazurite", "version", version)
            else:
                progress.log(
                    f"Ошибка при скачивании JAR файла. Статус код: {response.status_code}"
                )

        except Exception as e:
            progress.console.print(f"Ошибка: {e}")


@app.command("uninstall")
def uninstall_lazurite(version: Annotated[str, typer.Argument()]):
    if version not in get_release_versions():
        typer.echo("Версия не найдена.")
        raise typer.Exit()

    if not typer.confirm(f"Удалить Lazurite {version}? ", default=True):
        raise typer.Abort()

    typer.echo(f"Удаление Lazurite версии: {version}")
    lzr = Lzr()
    lazurite_path = lzr.path / "lazurite" / version
    shutil.rmtree(lazurite_path)


@app.command("version")
def lazurite_version():
    result = lazurite_run("-v")
    version = extract_version(result["stdout"])
    typer.echo(version)


@app.command("available")
def lazurite_available():
    api = LazuriteGithubApi()

    releases = api.get_all_releases().json()

    for release in releases:
        print(extract_version(release["tag_name"]))
