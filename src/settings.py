import os
from pathlib import Path
from rich.console import Console
from cachetools import Cache


VENV_NAME = ".lzr"

LZR_HOME = Path(os.getenv("LZR_HOME") or Path.home() / "lzr")

CONFIG_DIR_PATH = Path.home() / ".config" / "lzr"
CONFIG_FILE_NAME = "config.toml"
CONFIG_PATH = CONFIG_DIR_PATH / CONFIG_FILE_NAME

ENV_LAZURITE_VENV_PATH = "LAZURITE_VENV_PATH"
ENV_LAZURITE_JAR_PATH = "LAZURITE_JAR_PATH"

console = Console(log_path=False)
cache = Cache(1024)
