#!/usr/bin/env python3
"""Recalculate the SIP actual-effort planning snapshot from merged PR activity.

The normal documentation build deliberately does not call this script. It renders
from the committed snapshot in docs/_data/sip-roadmap.yaml.

This tool combines commit activity from both event-timing project repositories
into one chronological timeline before grouping work sessions.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import Iterable, List
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
SESSION_GAP_MINUTES = 90
SINGLE_COMMIT_MINUTES = 15
PROJECT_DAY_HOURS = 8.0


@dataclass(frozen=True)
class Activity:
    repository: str
    sha: str
    timestamp: datetime
    message: str


@dataclass(frozen=True)
class Session:
    start: datetime
    end: datetime
    activities: tuple[Activity, ...]
    hours: float


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


def group_sessions(activities: Iterable[Activity]) -> list[Session]:
    ordered = list(activities)
    if not ordered:
        return []

    gap_seconds = SESSION_GAP_MINUTES * 60
    groups: List[list[Activity]] = [[ordered[0]]]
    for activity in ordered[1:]:
        previous = groups[-1][-1]
        if (activity.timestamp - previous.timestamp).total_seconds() > gap_seconds:
            groups.append([activity])
        else:
            groups[-1].append(activity)

    sessions: list[Session] = []
    for group in groups:
        start = group[0].timestamp
        end = group[-1].timestamp
        if len(group) == 1:
            hours = SINGLE_COMMIT_MINUTES / 60.0
        else:
            hours = (end - start).total_seconds() / 3600.0
        sessions.append(
            Session(
                start=start,
                end=end,
                activities=tuple(group),
                hours=hours,
            )
        )
    return sessions


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
    sessions: list[Session],
) -> float:
    total_hours = sum(session.hours for session in sessions)
    project_days = total_hours / PROJECT_DAY_HOURS

    print("SIP actual-effort planning indication")
    print(f"Range:        {start.isoformat()} through {through.isoformat()}")
    print(f"Repositories: {', '.join(repositories)}")
    print(f"Commits:      {len(activities)} merged-PR commits")
    print(f"Sessions:     {len(sessions)}")
    print(f"Hours:        {total_hours:.2f}")
    print(f"Project days: {project_days:.2f} ({PROJECT_DAY_HOURS:g} h/day)")
    print()
    print("Sessions:")
    for index, session in enumerate(sessions, start=1):
        repo_names = sorted({item.repository.rsplit("/", 1)[-1] for item in session.activities})
        print(
            f"  {index:02d}  {session.start.isoformat()} -> {session.end.isoformat()}  "
            f"{session.hours:5.2f} h  {len(session.activities):3d} commits  "
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
    sessions = group_sessions(activities)
    project_days = print_report(
        PROJECT_REPOSITORIES,
        start,
        args.through,
        activities,
        sessions,
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
