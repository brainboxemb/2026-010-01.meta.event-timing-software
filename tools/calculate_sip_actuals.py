#!/usr/bin/env python3
"""Calculate the SIP actual-effort planning snapshot from GitHub PR commits."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
import argparse
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

import yaml


REPOSITORIES = (
    "brainboxemb/2026-010-01.meta.event-timing-software",
    "brainboxemb/2026-010-02.java.event-timing-framework",
)
PLAN_PATH = Path("docs/_data/sip-roadmap.yaml")
WINDOW_MINUTES = 30
PROJECT_DAY_HOURS = 8.0


def github_get(path: str, params: dict[str, object] | None = None):
    query = urllib.parse.urlencode(params or {})
    url = f"https://api.github.com{path}" + (f"?{query}" if query else "")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "event-timing-sip-actuals",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        if exc.code == 403 and not token:
            raise SystemExit(
                "GitHub API rate limit reached; set GITHUB_TOKEN or GH_TOKEN."
            ) from exc
        raise SystemExit(f"GitHub API request failed ({exc.code}): {detail}") from exc


def github_pages(path: str, params: dict[str, object] | None = None):
    page = 1
    while True:
        query = dict(params or {})
        query.update({"per_page": 100, "page": page})
        items = github_get(path, query)
        if not isinstance(items, list):
            raise SystemExit(f"Expected a list from GitHub API path {path}")
        yield from items
        if len(items) < 100:
            return
        page += 1


def timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(
        timezone.utc
    )


def merged_pr_numbers(repository: str, start: datetime, through: datetime) -> list[int]:
    numbers = []
    for pull in github_pages(
        f"/repos/{repository}/pulls",
        {"state": "closed", "sort": "updated", "direction": "desc"},
    ):
        merged_at = pull.get("merged_at")
        if merged_at and start <= timestamp(merged_at) <= through:
            numbers.append(int(pull["number"]))
    return numbers


def commit_times(repository: str, pull_number: int) -> list[tuple[str, datetime]]:
    result = []
    for commit in github_pages(
        f"/repos/{repository}/pulls/{pull_number}/commits"
    ):
        stamp = (
            commit.get("commit", {}).get("author", {}).get("date")
            or commit.get("commit", {}).get("committer", {}).get("date")
        )
        if stamp:
            result.append((commit["sha"], timestamp(stamp)))
    return result


def collect_activity(start: datetime, through: datetime) -> list[tuple[str, datetime]]:
    unique: dict[tuple[str, str], datetime] = {}
    for repository in REPOSITORIES:
        for pull_number in merged_pr_numbers(repository, start, through):
            for sha, commit_time in commit_times(repository, pull_number):
                if start <= commit_time <= through:
                    unique[(repository, sha)] = commit_time
    return sorted(
        ((repository, commit_time) for (repository, _), commit_time in unique.items()),
        key=lambda item: item[1],
    )


def activity_blocks(
    activity: list[tuple[str, datetime]],
) -> list[tuple[datetime, datetime, set[str], int]]:
    half_window = timedelta(minutes=WINDOW_MINUTES / 2)
    blocks: list[tuple[datetime, datetime, set[str], int]] = []

    for repository, commit_time in activity:
        start = commit_time - half_window
        end = commit_time + half_window

        if not blocks or start > blocks[-1][1]:
            blocks.append((start, end, {repository}, 1))
            continue

        old_start, old_end, repositories, count = blocks[-1]
        blocks[-1] = (
            old_start,
            max(old_end, end),
            repositories | {repository},
            count + 1,
        )

    return blocks


def update_snapshot(path: Path, through: date, project_days: float) -> None:
    text = path.read_text(encoding="utf-8")
    actuals = re.search(r"(?ms)^actuals:\n(?P<body>(?:^[ \t].*\n?)+)", text)
    if not actuals:
        raise SystemExit(f"Could not find actuals block in {path}")

    body = actuals.group("body")
    body = re.sub(
        r'(?m)^(  through_date:\s*)".*?"\s*$',
        lambda match: f'{match.group(1)}"{through.isoformat()}"',
        body,
        count=1,
    )
    body = re.sub(
        r"(?m)^(  estimated_project_days:\s*).*$",
        lambda match: f"{match.group(1)}{project_days:.1f}",
        body,
        count=1,
    )
    path.write_text(
        text[: actuals.start("body")] + body + text[actuals.end("body") :],
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Calculate SIP actual effort from merged-PR commit activity."
    )
    parser.add_argument("--plan", type=Path, default=PLAN_PATH)
    parser.add_argument("--through", type=date.fromisoformat, default=date.today())
    parser.add_argument(
        "--update",
        action="store_true",
        help="Write the rounded result to the roadmap YAML snapshot.",
    )
    args = parser.parse_args()

    plan = yaml.safe_load(args.plan.read_text(encoding="utf-8"))
    start_date = date.fromisoformat(str(plan["start_date"]))
    start = datetime.combine(start_date, time.min, tzinfo=timezone.utc)
    through = datetime.combine(args.through, time.max, tzinfo=timezone.utc)

    activity = collect_activity(start, through)
    blocks = activity_blocks(activity)
    total_hours = sum((end - start).total_seconds() for start, end, _, _ in blocks) / 3600
    project_days = total_hours / PROJECT_DAY_HOURS

    print("SIP actual-effort planning indication")
    print(f"Range:        {start_date} through {args.through}")
    print(f"Repositories: {', '.join(REPOSITORIES)}")
    print(f"Commits:      {len(activity)} merged-PR commits")
    print(f"Window:       {WINDOW_MINUTES} min per commit (±{WINDOW_MINUTES / 2:g} min)")
    print(f"Blocks:       {len(blocks)}")
    print(f"Hours:        {total_hours:.2f}")
    print(f"Project days: {project_days:.2f} ({PROJECT_DAY_HOURS:g} h/day)")
    print()
    print("Activity blocks:")
    for index, (start, end, repositories, count) in enumerate(blocks, start=1):
        names = ", ".join(sorted(repo.rsplit("/", 1)[-1] for repo in repositories))
        hours = (end - start).total_seconds() / 3600
        print(
            f"  {index:02d}  {start.isoformat()} -> {end.isoformat()}  "
            f"{hours:5.2f} h  {count:3d} commits  [{names}]"
        )

    if args.update:
        rounded = round(project_days, 1)
        update_snapshot(args.plan, args.through, rounded)
        print()
        print(
            f"Updated {args.plan}: through_date={args.through}, "
            f"estimated_project_days={rounded:.1f}"
        )


if __name__ == "__main__":
    main()
