from pathlib import Path
from typing import Any

import toml


class Config:
    def __init__(self, path: Path = Path(".")) -> None:
        self.path = path
        self.file_path = self.path / "config.toml"

    def create(self):
        if self.file_path.exists():
            return

        base_config = {
            "request": {
                "timeout": 100,
            }
        }

        with open(self.file_path, "w") as f:
            toml.dump(base_config, f)

    def get(self, table: str, key: str, default: Any = None):
        if not self.file_path.exists():
            self.create()

        with open(self.file_path, "r") as f:
            config = toml.load(f)

        return config.get(table, {}).get(key, default)

    def set(self, table: str, key: str, value: Any):
        if not self.file_path.exists():
            self.create()

        with open(self.file_path, "r") as f:
            config = toml.load(self.file_path)

        tbl: dict = config.get(table, {})
        tbl[key] = value

        config[table] = tbl

        with open(self.file_path, "w") as f:
            toml.dump(config, f)
