from .lazurite import app as lazurite_app
from .env import app as env_app

commands = [
    (lazurite_app, "lazurite"),
    (env_app, "env"),
]

__all__ = ["commands"]
