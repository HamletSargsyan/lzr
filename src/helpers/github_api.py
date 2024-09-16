import os

from cachetools import cached
import requests
import toml

from settings import cache, CONFIG_PATH


class GithubApi:
    def __init__(self, owner: str, repo: str) -> None:
        self.owner = owner
        self.repo = repo
        self.api_url = f"https://api.github.com/repos/{self.owner}/{self.repo}"

    @cached(cache)
    def _make_request(self, endpoint: str):
        headers = {
            "X-GitHub-Api-Version": "2022-11-28",
            "Accept": "application/vnd.github+json",
        }

        with open(CONFIG_PATH, "r") as f:
            timeout = toml.load(f).get("request", {}).get("timeout", 100)

        gh_token = os.environ.get("GITHUB_TOKEN", None)
        if gh_token:
            headers["Authorization"] = f"Bearer {gh_token}"
        return requests.get(
            f"{self.api_url}/{endpoint}", headers=headers, timeout=timeout
        )

    def get_all_releases(self):
        return self._make_request("releases")

    def get_release(self, version: str):
        if version == "latest":
            return self._make_request("releases/latest")
        return self._make_request(f"releases/tags/{version}")


class LazuriteGithubApi(GithubApi):
    def __init__(self) -> None:
        super().__init__("ArtyomKingmang", "Lazurite")


class SelfGithubApi(GithubApi):
    def __init__(self) -> None:
        super().__init__("HamletSargsyan", "lzr")
