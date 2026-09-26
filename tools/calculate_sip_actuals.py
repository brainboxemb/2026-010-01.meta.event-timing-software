#!/usr/bin/env python3
"""Recalculate the SIP actual-effort planning snapshot from merged PR activity.

The normal documentation build deliberately does not call this script. It renders
from the committed snapshot in docs/_data/sip-roadmap.yaml.

This tool combines commit activity from both event-timing project repositories
into one chronological timeline before grouping work sessions.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Iterable
import argparse
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

import yaml


PROJECT_REPOSITORIES = (
    "brainboxemb/2026-010-01.meta.event-timing-software",
    "brainboxemb/2026-010-02.java.event-timing-framework",
)
DEFAULT_PLAN = Path("docs/_data/sip-roadmap.yaml")
ACTIVITY_WINDOW_MINUTES = 30
PROJECT_DAY_HOURS = 8.0


@dataclass(frozen=True)
class Activity:
    repository: str
    sha: str
    timestamp: datetime
    message: str


@dataclass(frozen=True)
class ActivityBlock:
    start: datetime
    end: datetime
    activities: tuple[Activity, ...]

    @property
    def hours(self) -> float:
        return (self.end - self.start).total_seconds() / 3600.0


class GitHubClient:
    def __init__(self, token: str | None) -> None:
        self.token = token

    def get(self, path: str, params: dict[str, str | int] | None = None):
        query = urllib.parse.urlencode(params or {})
        url = f"https://api.github.com{path}"
        if query:
            url += f"?{query}"
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "event-timing-sip-actuals",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            if exc.code == 403 and not self.token:
                raise SystemExit(
                    "GitHub API rate limit reached. Set GITHUB_TOKEN or GH_TOKEN "
                    "and run the command again."
                ) from exc
            raise SystemExit(f"GitHub API request failed ({exc.code}): {detail}") from exc

    def pages(self, path: str, params: dict[str, str | int] | None = None):
        page = 1
        while True:
            page_params = dict(params or {})
            page_params.update({"per_page": 100, "page": page})
            items = self.get(path, page_params)
            if not isinstance(items, list):
                raise SystemExit(f"Expected a list from GitHub API path {path}")
            yield from items
            if len(items) < 100:
                break
            page += 1


def parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def day_start(value: date) -> datetime:
    return datetime.combine(value, time.min, tzinfo=timezone.utc)


def day_end_exclusive(value: date) -> datetime:
    return datetime.combine(value, time.max, tzinfo=timezone.utc)


def merged_pull_requests(
    client: GitHubClient,
    repository: str,
    start: datetime,
    through: datetime,
) -> list[dict]:
    pulls: list[dict] = []
    for pull in client.pages(
        f"/repos/{repository}/pulls",
        {"state": "closed", "sort": "updated", "direction": "asc"},
    ):
        merged_at = pull.get("merged_at")
        if not merged_at:
            continue
        merged = parse_timestamp(merged_at)
        if start <= merged <= through:
            pulls.append(pull)
    return pulls


def pull_activities(
    client: GitHubClient,
    repository: str,
    pull_number: int,
    start: datetime,
    through: datetime,
) -> list[Activity]:
    activities: list[Activity] = []
    for commit in client.pages(
        f"/repos/{repository}/pulls/{pull_number}/commits",
    ):
        stamp = (
            commit.get("commit", {}).get("author", {}).get("date")
            or commit.get("commit", {}).get("committer", {}).get("date")
        )
        if not stamp:
            continue
        timestamp = parse_timestamp(stamp)
        if not (start <= timestamp <= through):
            continue
        activities.append(
            Activity(
                repository=repository,
                sha=commit["sha"],
                timestamp=timestamp,
                message=commit.get("commit", {}).get("message", "").splitlines()[0],
            )
        )
    return activities


def collect_activities(
    client: GitHubClient,
    repositories: Iterable[str],
    start: datetime,
    through: datetime,
) -> list[Activity]:
    unique: dict[tuple[str, str], Activity] = {}
    for repository in repositories:
        pulls = merged_pull_requests(client, repository, start, through)
        for pull in pulls:
            for activity in pull_activities(
                client, repository, int(pull["number"]), start, through
            ):
                unique[(activity.repository, activity.sha)] = activity
    return sorted(unique.values(), key=lambda item: item.timestamp)


def merge_activity_windows(activities: Iterable[Activity]) -> list[ActivityBlock]:
    ordered = list(activities)
    if not ordered:
        return []

    half_window = timedelta(minutes=ACTIVITY_WINDOW_MINUTES / 2.0)
    blocks: list[ActivityBlock] = []

    for activity in ordered:
        window_start = activity.timestamp - half_window
        window_end = activity.timestamp + half_window

        if not blocks or window_start > blocks[-1].end:
            blocks.append(
                ActivityBlock(
                    start=window_start,
                    end=window_end,
                    activities=(activity,),
                )
            )
            continue

        previous = blocks[-1]
        blocks[-1] = ActivityBlock(
            start=previous.start,
            end=max(previous.end, window_end),
            activities=previous.activities + (activity,),
        )

    return blocks


def update_plan_snapshot(path: Path, through: date, project_days: float) -> None:
    text = path.read_text(encoding="utf-8")
    actuals_match = re.search(r"(?ms)^actuals:\n(?P<body>(?:^[ \t].*\n?)+)", text)
    if not actuals_match:
        raise SystemExit(f"Could not find actuals block in {path}")

    body = actuals_match.group("body")
    body = re.sub(
        r'(?m)^(  through_date:\s*)".*?"\s*$',
        rf'\1"{through.isoformat()}"',
        body,
        count=1,
    )
    body = re.sub(
        r"(?m)^(  estimated_project_days:\s*).*$",
        rf"\1{project_days:.1f}",
        body,
        count=1,
    )
    updated = text[: actuals_match.start("body")] + body + text[actuals_match.end("body") :]
    path.write_text(updated, encoding="utf-8")


def print_report(
    repositories: tuple[str, ...],
    start: date,
    through: date,
    activities: list[Activity],
    blocks: list[ActivityBlock],
) -> float:
    total_hours = sum(block.hours for block in blocks)
    project_days = total_hours / PROJECT_DAY_HOURS

    print("SIP actual-effort planning indication")
    print(f"Range:        {start.isoformat()} through {through.isoformat()}")
    print(f"Repositories: {', '.join(repositories)}")
    print(f"Commits:      {len(activities)} merged-PR commits")
    print(f"Window:       {ACTIVITY_WINDOW_MINUTES:g} min per commit (±{ACTIVITY_WINDOW_MINUTES / 2:g} min)")
    print(f"Blocks:       {len(blocks)} merged activity windows")
    print(f"Hours:        {total_hours:.2f}")
    print(f"Project days: {project_days:.2f} ({PROJECT_DAY_HOURS:g} h/day)")
    print()
    print("Activity blocks:")
    for index, block in enumerate(blocks, start=1):
        repo_names = sorted({item.repository.rsplit("/", 1)[-1] for item in block.activities})
        print(
            f"  {index:02d}  {block.start.isoformat()} -> {block.end.isoformat()}  "
            f"{block.hours:5.2f} h  {len(block.activities):3d} commits  "
            f"[{', '.join(repo_names)}]"
        )
    return project_days


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Calculate the SIP actual-effort snapshot from merged PR commits."
    )
    parser.add_argument(
        "--plan",
        type=Path,
        default=DEFAULT_PLAN,
        help=f"Roadmap YAML (default: {DEFAULT_PLAN})",
    )
    parser.add_argument(
        "--through",
        type=date.fromisoformat,
        default=date.today(),
        help="Inclusive snapshot date in YYYY-MM-DD form (default: today)",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update actuals.through_date and estimated_project_days in the roadmap YAML.",
    )
    args = parser.parse_args()

    plan = yaml.safe_load(args.plan.read_text(encoding="utf-8"))
    start = date.fromisoformat(str(plan["start_date"]))
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    client = GitHubClient(token)

    start_dt = day_start(start)
    through_dt = day_end_exclusive(args.through)
    activities = collect_activities(
        client,
        PROJECT_REPOSITORIES,
        start_dt,
        through_dt,
    )
    blocks = merge_activity_windows(activities)
    project_days = print_report(
        PROJECT_REPOSITORIES,
        start,
        args.through,
        activities,
        blocks,
    )

    if args.update:
        rounded = round(project_days, 1)
        update_plan_snapshot(args.plan, args.through, rounded)
        print()
        print(
            f"Updated {args.plan}: through_date={args.through.isoformat()}, "
            f"estimated_project_days={rounded:.1f}"
        )


if __name__ == "__main__":
    main()
