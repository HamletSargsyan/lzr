import re
from pathlib import Path

import toml
from typing_extensions import Annotated
import typer

from commands import commands
from helpers.utils import (
    compare_versions,
    lazurite_run,
    print_run_result,
)
from core import Lzr

app = typer.Typer()
for command in commands:
    app.add_typer(command[0], name=command[1])


# Основные команды
@app.command("run")
def run(file: Annotated[str, typer.Argument()] = ""):
    lzr = Lzr()
    version = lzr.get_lazurite_version()

    if file:
        result = lazurite_run("-r", file)
        print_run_result(result)
    else:
        with open("project.toml") as f:
            project_toml = toml.load(f)

        if project_toml.get("lib_file", None) is not None:
            raise NotImplementedError  # TODO

        if compare_versions(version, "2.7.4") >= 0:
            result = lazurite_run("-r")
            print_run_result(result)
        else:
            raise NotImplementedError  # TODO


@app.command()
def create(name: str, lib: bool = False):
    path = Path(name)

    if path.exists():
        return  # TODO

    if not re.fullmatch(r"^[a-z0-9\\-]+$", name):
        print("Name of project should contain only `a-z`, `0-9` and `-`")
        return  # TODO

    path.mkdir()
    project_toml_content = {"package": {"name": name, "version": "0.1.0"}}

    if lib:
        project_toml_content["package"]["lib_file"] = "src/lib.lzr"
    else:
        project_toml_content["package"]["run_file"] = "src/main.lzr"

    project_toml_path = path / "project.toml"
    project_toml_path.touch()
    with open(project_toml_path, "w") as f:
        toml.dump(project_toml_content, f)

    src_path = path / "src"
    src_path.mkdir()

    file_path = src_path / ("lib.lzr" if lib else "main.lzr")
    file_path.touch()

    with open(file_path, "w") as f:
        f.write('println("Hello, world!")\n\n')

@app.command()
def versions():
    lzr = Lzr()


    for version in lzr.get_all_versions():
        _prefix = ""
        if version == lzr.get_lazurite_version():
            _prefix = "(current)"
        print(f"{version} {_prefix}")

def main():
    app()


if __name__ == "__main__":
    main()
