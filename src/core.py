from pathlib import Path
from helpers.config import Config
from settings import VERSION_FILE_NAME


class Lzr:
    _instance = None

    def __new__(cls, *args, **kwargs) -> "Lzr":
        if cls._instance is None:
            cls._instance = super(Lzr, cls).__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self, path: Path = Path.home()) -> None:
        if self.__initialized:
            return
        self.path = path / ".lzr"
        self.config = Config(path).create()
        self.__initialized = True

        self.path.mkdir(exist_ok=True)
        (self.path / "lazurite").mkdir(exist_ok=True)

    def get_lazurite_version(self) -> str:
        local_version = Path(VERSION_FILE_NAME)
        if local_version.exists():
            with open(VERSION_FILE_NAME) as f:
                from helpers.utils import extract_version

                return extract_version(f.read())

        return self.get_global_version()

    def get_global_version(self) -> str:
        return self.config.get(
            "lazurite", "version", self.get_installed_biggest_version()
        )

    def get_all_versions(self) -> list[str]:
        from helpers.utils import extract_version, sort_versions

        def _():
            for version in (self.path / "lazurite").iterdir():
                yield extract_version(str(version))

        return sort_versions(list(_()))

    def get_installed_biggest_version(self) -> str:
        from helpers.utils import sort_versions

        try:
            return sort_versions(self.get_all_versions())[-1]
        except IndexError:
            raise RuntimeError("Не установлено ни одной версии Lazurite.")

    def get_jar_path(self) -> Path:
        path = self.path / "lazurite" / self.get_lazurite_version() / "lazurite.jar"
        if not path.exists():
            raise FileNotFoundError(f"JAR файл не найден по пути {path}")
        return path
