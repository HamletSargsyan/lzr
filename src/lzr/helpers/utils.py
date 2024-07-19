import os
import re
from pathlib import Path
import subprocess
from typing import Any, TypedDict

from cachetools import cached
from helpers.venv import Venv
from settings import (
    cache,
    ENV_LAZURITE_VENV_PATH,
    DEFAULT_LAZURITE_VENV_PATH,
)
from helpers.github_api import LazuriteGithubApi


VERSION_PATTERN = re.compile(r"(\d+\.\d+(\.\d+)?)")


def get_venv_path():
    venv_path = os.environ.get(ENV_LAZURITE_VENV_PATH)
    if venv_path and Path(venv_path).exists():
        return Venv(Path(venv_path)).create()
    elif Path(DEFAULT_LAZURITE_VENV_PATH).exists():
        return Venv().create()
    raise  # TODO


@cached(cache)
def extract_version(text: str) -> str:
    match = VERSION_PATTERN.search(text)
    return match.group(0) if match else ""


def get_version_from_release(release: dict[str, Any]):
    version = extract_version(release["tag_name"])
    if not version:
        version = extract_version(release["name"])
    return version


def get_release_versions():
    api = LazuriteGithubApi()

    def work():
        for release in api.get_all_releases().json():
            yield get_version_from_release(release)

    return list(work())


@cached(cache)
def get_release_by_version(version: str):
    api = LazuriteGithubApi()
    if version == "2.5":
        tag_name = "lazurite"
    elif version == "latest":
        return api.get_release("latest")
    elif not version.startswith("lazurite"):
        tag_name = f"lazurite-{version}"
    else:
        tag_name = version

    return api.get_release(tag_name)


def compare_versions(version1: str, version2: str) -> int:
    """
    Сравнивает две версии в виде строки.

    :param version1: Первая версия в формате "X.Y.Z".
    :param version2: Вторая версия в формате "X.Y.Z".
    :return: -1, если версия1 < версия2; 1, если версия1 > версия2; 0, если версии равны.
    """
    v1_parts = list(map(int, version1.split(".")))
    v2_parts = list(map(int, version2.split(".")))

    # Приводим версии к одинаковой длине, добавляя нули
    max_length = max(len(v1_parts), len(v2_parts))
    v1_parts.extend([0] * (max_length - len(v1_parts)))
    v2_parts.extend([0] * (max_length - len(v2_parts)))

    # Сравниваем каждую часть версий
    for v1, v2 in zip(v1_parts, v2_parts):
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1

    return 0


def sort_versions(versions: list[str]) -> list[str]:
    """
    Сортирует список версий в формате "X.Y.Z".

    :param versions: Список версий.
    :return: Отсортированный список версий.
    """
    return sorted(
        versions, key=lambda version: [int(part) for part in version.split(".")]
    )





class RunResult(TypedDict):
    stdout: str
    stderr: str


def lazurite_run(*args: str) -> RunResult:
    venv = get_venv_path()
    version = venv.get_version()
    jar_path = venv.get_jar_path()

    if compare_versions(version, "2.7.4") >= 0:
        result = subprocess.run(
            ("java", "-jar", jar_path, *args),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout = result.stdout if result.stdout else ""
        stderr = result.stderr if result.stderr else ""
    else:
        process = subprocess.Popen(
            ("java", "-jar", jar_path),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate(" ".join(args))

    return {
        "stdout": stdout,
        "stderr": stderr,
    }


def print_run_result(result: RunResult):
    if result["stdout"]:
        print(result["stdout"])
    if result["stderr"]:
        print(result["stderr"])

