#!/usr/bin/env python3
"""Fetch GitHub Trending repositories and save each project as one Markdown file."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone, tzinfo
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import requests
from bs4 import BeautifulSoup


TRENDING_URL = "https://github.com/trending"
GITHUB_URL = "https://github.com"
GITHUB_API_URL = "https://api.github.com"
DEFAULT_TIMEZONE = "Asia/Shanghai"
PERIODS = {
    "today": "daily",
    "this_week": "weekly",
    "this_month": "monthly",
}
README_CANDIDATES = (
    "README.md",
    "README.rst",
    "README.txt",
    "README.adoc",
    "README",
)
BRANCH_CANDIDATES = ("main", "master", "develop", "trunk")


@dataclass(frozen=True)
class TrendingRepo:
    owner: str
    name: str
    url: str
    description: str
    period: str

    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.name}"


class GitHubTrendingFetcher:
    def __init__(
        self,
        output_dir: Path,
        token: str | None = None,
        delay: float = 0.5,
        snapshot_date: str | None = None,
        timezone_name: str = DEFAULT_TIMEZONE,
        timeout: int = 30,
    ) -> None:
        self.output_dir = output_dir
        self.delay = delay
        self.timezone_name = timezone_name
        self.timezone = parse_timezone(timezone_name)
        self.snapshot_date = snapshot_date or local_date_iso(self.timezone)
        self.timeout = timeout
        self.index_path = output_dir / "index.json"
        self.index = self.load_index()
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "github-trending-readme-fetcher/1.0",
            }
        )
        self.api_headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "github-trending-readme-fetcher/1.0",
        }
        if token:
            self.api_headers["Authorization"] = f"Bearer {token}"

    def fetch_all(self, periods: Iterable[str], limit: int | None = None) -> list[Path]:
        written_files: list[Path] = []
        for period in periods:
            repos = self.fetch_trending(period)
            if limit is not None:
                repos = repos[:limit]
            print(f"[{period}] found {len(repos)} repositories", file=sys.stderr)

            snapshot_repos: list[dict[str, object]] = []
            for index, repo in enumerate(repos, start=1):
                print(f"[{period}] ({index}/{len(repos)}) {repo.full_name}", file=sys.stderr)
                readme = self.fetch_readme(repo.owner, repo.name)
                readme_hash = sha256_text(readme)
                project_path = self.save_project(repo, readme, readme_hash)
                if project_path:
                    written_files.append(project_path)
                project_path = self.project_path(repo)
                self.update_index(repo, readme_hash, project_path)
                snapshot_repos.append(
                    self.snapshot_entry(
                        rank=index,
                        repo=repo,
                        readme_hash=readme_hash,
                        project_path=project_path,
                    )
                )
                time.sleep(self.delay)
            snapshot_path = self.save_snapshot(period, snapshot_repos)
            if snapshot_path:
                written_files.append(snapshot_path)

        if write_json_if_changed(self.index_path, self.index):
            written_files.append(self.index_path)
        return written_files

    def fetch_trending(self, period: str) -> list[TrendingRepo]:
        since = PERIODS[period]
        response = self.session.get(
            TRENDING_URL,
            params={"since": since},
            timeout=self.timeout,
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        repos: list[TrendingRepo] = []
        for article in soup.select("article.Box-row"):
            repo_link = article.select_one("h2 a[href]")
            if not repo_link:
                continue

            href = repo_link["href"].strip()
            parts = [part for part in href.strip("/").split("/") if part]
            if len(parts) < 2:
                continue

            desc_el = article.select_one("p")
            description = normalize_text(desc_el.get_text(" ", strip=True)) if desc_el else ""
            owner, name = parts[0], parts[1]
            repos.append(
                TrendingRepo(
                    owner=owner,
                    name=name,
                    url=urljoin(GITHUB_URL, href),
                    description=description,
                    period=period,
                )
            )
        return repos

    def fetch_readme(self, owner: str, repo: str) -> str:
        api_readme = self.fetch_readme_from_api(owner, repo)
        if api_readme:
            return api_readme

        raw_readme = self.fetch_readme_from_raw(owner, repo)
        if raw_readme:
            return raw_readme

        return "README not found or could not be fetched."

    def fetch_readme_from_api(self, owner: str, repo: str) -> str | None:
        url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/readme"
        response = self.session.get(url, headers=self.api_headers, timeout=self.timeout)
        if response.status_code in {403, 404}:
            return None
        response.raise_for_status()

        payload = response.json()
        content = payload.get("content")
        encoding = payload.get("encoding")
        if content and encoding == "base64":
            return base64.b64decode(content).decode("utf-8", errors="replace")

        download_url = payload.get("download_url")
        if download_url:
            raw = self.session.get(download_url, timeout=self.timeout)
            if raw.ok:
                return raw.text
        return None

    def fetch_readme_from_raw(self, owner: str, repo: str) -> str | None:
        for branch in BRANCH_CANDIDATES:
            for filename in README_CANDIDATES:
                url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{filename}"
                response = self.session.get(url, timeout=self.timeout)
                if response.ok and response.text.strip():
                    return response.text
        return None

    def save_project(self, repo: TrendingRepo, readme: str, readme_hash: str) -> Path | None:
        path = self.project_path(repo)
        metadata = {
            "owner": repo.owner,
            "name": repo.name,
            "full_name": repo.full_name,
            "url": repo.url,
            "description": repo.description,
            "readme_sha256": readme_hash,
        }
        front_matter = json.dumps(metadata, ensure_ascii=False, indent=2)
        body = (
            "```json\n"
            f"{front_matter}\n"
            "```\n\n"
            f"# {repo.full_name}\n\n"
            f"- URL: {repo.url}\n"
            f"- Description: {repo.description or 'No description'}\n"
            f"- README SHA256: `{readme_hash}`\n\n"
            "## README\n\n"
            f"{readme.rstrip()}\n"
        )
        return path if write_text_if_changed(path, body) else None

    def project_path(self, repo: TrendingRepo) -> Path:
        filename = f"{safe_name(repo.owner)}__{safe_name(repo.name)}.md"
        return self.output_dir / "projects" / filename

    def snapshot_entry(
        self,
        rank: int,
        repo: TrendingRepo,
        readme_hash: str,
        project_path: Path,
    ) -> dict[str, object]:
        return {
            "rank": rank,
            "full_name": repo.full_name,
            "url": repo.url,
            "description": repo.description,
            "project_file": str(project_path.relative_to(self.output_dir)),
            "readme_sha256": readme_hash,
        }

    def save_snapshot(self, period: str, repos: list[dict[str, object]]) -> Path | None:
        path = self.output_dir / "snapshots" / self.snapshot_date / f"{period}.json"
        snapshot = {
            "snapshot_date": self.snapshot_date,
            "timezone": self.timezone_name,
            "period": period,
            "github_since": PERIODS[period],
            "source_url": TRENDING_URL,
            "repositories": repos,
        }
        return path if write_json_if_changed(path, snapshot) else None

    def load_index(self) -> dict[str, object]:
        if not self.index_path.exists():
            return {"schema_version": 1, "repositories": {}}

        with self.index_path.open(encoding="utf-8") as handle:
            index = json.load(handle)
        if not isinstance(index, dict) or not isinstance(index.get("repositories"), dict):
            raise ValueError(f"invalid index file: {self.index_path}")
        return index

    def update_index(self, repo: TrendingRepo, readme_hash: str, project_path: Path) -> None:
        repositories = self.index["repositories"]
        if not isinstance(repositories, dict):
            raise ValueError(f"invalid repositories object in {self.index_path}")

        record = repositories.setdefault(
            repo.full_name,
            {
                "owner": repo.owner,
                "name": repo.name,
                "url": repo.url,
                "first_seen": self.snapshot_date,
                "last_seen": self.snapshot_date,
                "seen": [],
                "readme_changes": [],
            },
        )
        if not isinstance(record, dict):
            raise ValueError(f"invalid repository record for {repo.full_name}")

        record.update(
            {
                "owner": repo.owner,
                "name": repo.name,
                "url": repo.url,
                "description": repo.description,
                "last_seen": self.snapshot_date,
                "project_file": str(project_path.relative_to(self.output_dir)),
            }
        )
        seen = record.setdefault("seen", [])
        observation = {"date": self.snapshot_date, "period": repo.period}
        if observation not in seen:
            seen.append(observation)

        if record.get("latest_readme_sha256") != readme_hash:
            changes = record.setdefault("readme_changes", [])
            changes.append({"date": self.snapshot_date, "sha256": readme_hash})
            record["latest_readme_sha256"] = readme_hash


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-") or "unknown"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def local_date_iso(date_timezone: tzinfo) -> str:
    return datetime.now(date_timezone).date().isoformat()


def write_text_if_changed(path: Path, content: str) -> bool:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def write_json_if_changed(path: Path, payload: dict[str, object]) -> bool:
    content = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return write_text_if_changed(path, content)


def snapshot_date(value: str) -> str:
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD format") from exc
    return value


def parse_timezone(value: str) -> tzinfo:
    normalized = value.strip()
    if normalized.upper() in {"Z", "UTC"}:
        return timezone.utc

    offset_match = re.fullmatch(
        r"(?:UTC)?([+-])(\d{1,2})(?::?(\d{2}))?",
        normalized,
        flags=re.IGNORECASE,
    )
    if offset_match:
        sign, hours, minutes = offset_match.groups()
        hour_value = int(hours)
        minute_value = int(minutes or "0")
        if hour_value > 23 or minute_value > 59:
            raise ValueError("UTC offset out of range")
        delta = timedelta(hours=hour_value, minutes=minute_value)
        if sign == "-":
            delta = -delta
        return timezone(delta)

    try:
        return ZoneInfo(normalized)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"unknown timezone: {value}") from exc


def timezone_arg(value: str) -> str:
    try:
        parse_timezone(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch GitHub Trending repositories for today, this week, and this month.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/github_trending"),
        help="Directory where project Markdown files are written.",
    )
    parser.add_argument(
        "--period",
        choices=tuple(PERIODS.keys()),
        action="append",
        help="Period to fetch. Can be repeated. Defaults to all periods.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional max repositories to save per period, useful for testing.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Delay in seconds between README requests.",
    )
    parser.add_argument(
        "--snapshot-date",
        type=snapshot_date,
        default=None,
        help="Snapshot date in YYYY-MM-DD format. Overrides --timezone date calculation.",
    )
    parser.add_argument(
        "--timezone",
        type=timezone_arg,
        default=DEFAULT_TIMEZONE,
        help=(
            "Timezone used to calculate snapshot date. Supports IANA names "
            "like Asia/Shanghai or UTC offsets like +08:00. Defaults to Asia/Shanghai."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    periods = args.period or list(PERIODS.keys())
    token = os.environ.get("GITHUB_TOKEN")

    fetcher = GitHubTrendingFetcher(
        output_dir=args.output_dir,
        token=token,
        delay=args.delay,
        snapshot_date=args.snapshot_date,
        timezone_name=args.timezone,
    )
    written_files = fetcher.fetch_all(periods=periods, limit=args.limit)
    print(f"wrote or updated {len(written_files)} files under {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
