# GitHub Trending Fetcher

[中文](README.md)

Fetch GitHub Trending daily, weekly, and monthly repositories, then save each repository's URL, description, and README locally.

## Features

- Fetches the daily, weekly, and monthly GitHub Trending lists.
- Saves each unique repository as one Markdown file to avoid duplicated README content.
- Stores daily snapshots with date, rank, repository reference, and README hash.
- Maintains `index.json` with first seen date, last seen date, seen history, and README changes.
- Supports configurable timezone. The default is `Asia/Shanghai`.

## Installation

```bash
pip install -r requirements.txt
```

Optional: set `GITHUB_TOKEN` to increase the GitHub API rate limit.

```bash
export GITHUB_TOKEN=your_token
```

## Usage

Fetch all three lists and write to `data/github_trending`:

```bash
python fetch_github_trending.py
```

Recommended explicit output directory:

```bash
python fetch_github_trending.py --output-dir data/github_trending
```

Fetch only one list:

```bash
python fetch_github_trending.py --period today
python fetch_github_trending.py --period this_week
python fetch_github_trending.py --period this_month
```

Limit repositories per period for testing:

```bash
python fetch_github_trending.py --limit 3
```

## Data Layout

```text
data/github_trending/
  projects/
    owner__repo.md
  snapshots/
    2026-05-22/
      today.json
      this_week.json
      this_month.json
  index.json
```

Files:

- `projects/owner__repo.md`: repository detail file with URL, description, README, and README SHA256.
- `snapshots/YYYY-MM-DD/*.json`: daily ranking snapshots with rank, repository reference, and README SHA256.
- `index.json`: global index with `first_seen`, `last_seen`, `seen`, `latest_readme_sha256`, and `readme_changes`.

## Date and Timezone

The snapshot date is calculated with `Asia/Shanghai` by default.

```bash
python fetch_github_trending.py --timezone Asia/Shanghai
python fetch_github_trending.py --timezone +08:00
```

`--timezone` supports IANA timezone names and UTC offsets:

```bash
python fetch_github_trending.py --timezone UTC
python fetch_github_trending.py --timezone America/Los_Angeles
python fetch_github_trending.py --timezone UTC+08:00
```

Set the saved snapshot date manually:

```bash
python fetch_github_trending.py --snapshot-date 2026-05-22
```

Note: `--snapshot-date` is only a local label for saved data. It cannot fetch historical GitHub Trending results. GitHub Trending only exposes the current daily, weekly, and monthly pages.

## Deduplication and Updates

Run the same command every day:

```bash
python fetch_github_trending.py --output-dir data/github_trending --timezone Asia/Shanghai
```

On repeated runs:

- Daily snapshots are saved under `snapshots/YYYY-MM-DD/`.
- Each repository is saved once under `projects/`.
- Repository Markdown files are rewritten only when the description or README content changes.
- README changes are detected by SHA256 and recorded in `index.json` under `readme_changes`.

## GitHub Actions

This repository includes a workflow:

```text
.github/workflows/fetch-github-trending.yml
```

It runs daily and also supports manual dispatch. The workflow fetches data and commits changes under `data/github_trending`.

## Options

```text
--output-dir       Output directory. Default: data/github_trending
--period           Trending list to fetch. Can be repeated: today, this_week, this_month
--limit            Max repositories per list, useful for testing
--delay            Delay between README requests. Default: 0.5 seconds
--snapshot-date    Manually set saved snapshot date, format YYYY-MM-DD
--timezone         Timezone used to calculate snapshot date. Default: Asia/Shanghai
```
