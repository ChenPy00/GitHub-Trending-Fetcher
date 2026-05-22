# GitHub Trending Fetcher

[English](README_EN.md)

抓取 GitHub Trending 的今日、本周、本月榜单，获取项目 URL、简介和 README，并保存到本地。

## 功能

- 抓取 GitHub Trending 的今日、本周、本月榜单。
- 每个唯一项目只保存一份 Markdown 文件，避免同一项目在多个榜单中重复保存。
- 每天保存榜单快照，保留日期、排名、项目引用和 README 哈希。
- 维护 `index.json`，记录项目首次出现、最后出现、出现历史和 README 变更。
- 支持自定义时区，默认 `Asia/Shanghai`。

## 安装

```bash
pip install -r requirements.txt
```

可选：设置 `GITHUB_TOKEN` 以提高 GitHub API 限额。

```bash
export GITHUB_TOKEN=your_token
```

## 使用

默认抓取三个榜单，并输出到 `data/github_trending`：

```bash
python fetch_github_trending.py
```

推荐显式指定输出目录：

```bash
python fetch_github_trending.py --output-dir data/github_trending
```

只抓取某个榜单：

```bash
python fetch_github_trending.py --period today
python fetch_github_trending.py --period this_week
python fetch_github_trending.py --period this_month
```

测试时限制每个时间范围的项目数量：

```bash
python fetch_github_trending.py --limit 3
```

## 数据结构

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

说明：

- `projects/owner__repo.md`：项目详情文件，包含 URL、简介、README 和 README SHA256。
- `snapshots/YYYY-MM-DD/*.json`：每日榜单快照，包含排名、项目引用和 README SHA256。
- `index.json`：全局索引，包含 `first_seen`、`last_seen`、`seen`、`latest_readme_sha256` 和 `readme_changes`。

## 日期和时区

脚本默认按 `Asia/Shanghai` 计算快照日期，也就是东八区。

```bash
python fetch_github_trending.py --timezone Asia/Shanghai
python fetch_github_trending.py --timezone +08:00
```

`--timezone` 支持 IANA 时区名和 UTC offset：

```bash
python fetch_github_trending.py --timezone UTC
python fetch_github_trending.py --timezone America/Los_Angeles
python fetch_github_trending.py --timezone UTC+08:00
```

如果需要手动指定保存日期：

```bash
python fetch_github_trending.py --snapshot-date 2026-05-22
```

注意：`--snapshot-date` 只是保存日期标签，不能获取历史 GitHub Trending。GitHub Trending 官方页面只返回当前的 daily、weekly、monthly 榜单。

## 去重和更新

每天运行同一条命令即可：

```bash
python fetch_github_trending.py --output-dir data/github_trending --timezone Asia/Shanghai
```

重复运行时：

- 当天快照保存在 `snapshots/YYYY-MM-DD/`。
- 同一项目只保存到 `projects/` 一次。
- 项目文件只有在简介或 README 内容变化时才会重写。
- README 是否变化由 SHA256 判断，并记录到 `index.json` 的 `readme_changes`。

## GitHub Actions

仓库已包含 workflow：

```text
.github/workflows/fetch-github-trending.yml
```

它会每天运行一次，也支持手动触发。workflow 会抓取数据并提交 `data/github_trending` 下的变化。

## 常用参数

```text
--output-dir       输出目录，默认 data/github_trending
--period           榜单类型，可重复传入：today、this_week、this_month
--limit            每个榜单最多保存多少个项目，适合测试
--delay            README 请求间隔，默认 0.5 秒
--snapshot-date    手动指定保存日期，格式 YYYY-MM-DD
--timezone         用于计算保存日期的时区，默认 Asia/Shanghai
```
