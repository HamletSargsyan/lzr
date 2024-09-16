from pathlib import Path

from helpers.config import Config


class Venv:
    def __init__(self, path: Path = Path.home()) -> None:
        self.path = (path if isinstance(path, Path) else Path(path)) / ".lzr"
        self.config = Config(path)

    def create(self):
        self.path.mkdir(exist_ok=True)

        lazurite_folder = self.path / "lazurite"
        lazurite_folder.mkdir(exist_ok=True)

        self.config.create()
        return self

    def get_version(self) -> str:
        return self.config.get(
            "lazurite", "version", self.get_installed_biggest_version()
        )

    def set_version(self, version: str):
        self.config.set("lazurite", "version", version)

    def get_all_versions(self) -> list[str]:
        from helpers.utils import extract_version

        def work():
            for version in (self.path / "lazurite").iterdir():
                yield extract_version(str(version))

        return list(work())

    def get_installed_biggest_version(self) -> str:
        from helpers.utils import sort_versions

        try:
            return sort_versions(self.get_all_versions())[-1]
        except IndexError:
            raise  # TODO

    def get_jar_path(self) -> Path:
        path = self.path / "lazurite" / self.get_version() / "lazurite.jar"
        if not path.exists():
            raise NotImplementedError  # TODO
        return path
