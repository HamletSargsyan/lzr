import os
from pathlib import Path
from rich.console import Console
from cachetools import Cache


VERSION_FILE_NAME = ".lazurite-version"

LZR_HOME = Path(os.getenv("LZR_HOME") or Path.home() / ".lzr")

CONFIG_DIR_PATH = Path.home() / ".config" / "lzr"
CONFIG_FILE_NAME = "config.toml"
CONFIG_PATH = CONFIG_DIR_PATH / CONFIG_FILE_NAME

ENV_LAZURITE_VENV_PATH = "LAZURITE_VENV_PATH"
ENV_LAZURITE_JAR_PATH = "LAZURITE_JAR_PATH"

console = Console(log_path=False)
cache = Cache(1024)

LZR_HOME.mkdir(parents=True, exist_ok=True)
CONFIG_DIR_PATH.mkdir(parents=True, exist_ok=True)
