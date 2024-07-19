import shutil
from typing import Any

import toml
import typer
import requests
from rich.progress import Progress

from settings import CONFIG_PATH, console
from helpers.utils import (
    extract_version,
    get_release_by_version,
    get_release_versions,
    get_venv_path,
    get_version_from_release,
    lazurite_run,
)

app = typer.Typer()


@app.command("install")
def install_lazurite(version: str = "latest"):
    venv_path = get_venv_path()
    

    with Progress(console=console) as progress:
        _task_fetching = progress.add_task("Fetching GitHub", total=100)
        progress.console.log(f"Installing Lazurite version: {version}")
        try:
            _release = get_release_by_version(version)
            if _release.status_code == 404:
                _release.raise_for_status()
            release: dict[str, Any] = _release.json()
            progress.update(_task_fetching, advance=100)

            progress.console.log("Done")
        except Exception as e:
            progress.console.print(f"Error: {e}")
            return

        version = get_version_from_release(release)

        assets = release.get("assets", [])
        jar_url = None
        for asset in assets:
            if asset["name"].endswith(".jar"):
                jar_url = asset["browser_download_url"]
                break

        if not jar_url:
            typer.echo("JAR file not found in the release assets.")
            return

        path = venv_path.path / "lazurite" / f"{version}"
        path.mkdir(exist_ok=True)
        jar_path = venv_path.get_jar_path()

        progress.log(f"Downloading Lazurite JAR from {jar_url} to {jar_path}")

        try:
            response = requests.get(jar_url, stream=True)
            total_length = int(response.headers.get("content-length", 0))

            if response.status_code == 200:
                with open(jar_path, "wb") as file:
                    download_task = progress.add_task("Downloading", total=total_length)
                    for chunk in response.iter_content(chunk_size=4096):
                        file.write(chunk)
                        progress.update(download_task, advance=len(chunk))
                progress.log("Lazurite JAR downloaded successfully.")
            else:
                progress.log(
                    f"Failed to download JAR file. Status code: {response.status_code}"
                )
        except Exception as e:
            progress.log(f"Error during download: {e}")


@app.command("use")
def use_lazurite(version: str):
    if version not in get_release_versions():
        return  # TODO
    typer.echo(f"Using Lazurite version: {version}")
    with open(CONFIG_PATH, "r") as f:
        config = toml.load(f)
        config["lazurite"] = {"version": version}

        with open(CONFIG_PATH, "w") as f:
            toml.dump(config, f)


@app.command("uninstall")
def uninstall_lazurite(version: str):
    if version not in get_release_versions():
        raise NotImplementedError  # TODO

    if not typer.confirm(f"Delete lazurite {version}? ", default=True):
        raise typer.Abort()

    typer.echo(f"Uninstalling Lazurite version: {version}")

    venv = get_venv_path()
    lazurite_path = venv.path / "lazurite" / version
    shutil.rmtree(lazurite_path)


@app.command("version")
def lazurite_version():
    stdout = lazurite_run("-v")["stdout"]
    version = extract_version(stdout)
    typer.echo(version)
