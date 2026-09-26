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


def step_for_pr(repository: str, pull_number: int, plan: dict) -> int | None:
    ranges = plan["actuals"]["step_pr_attribution"].get(repository, {})
    matches = []
    for step_text, bounds in ranges.items():
        first = int(bounds["first_pr"])
        last = bounds.get("last_pr")
        if pull_number >= first and (last is None or pull_number <= int(last)):
            matches.append(int(step_text))
    if len(matches) > 1:
        raise SystemExit(
            f"PR attribution overlaps for {repository}#{pull_number}: steps {matches}"
        )
    return matches[0] if matches else None


def collect_activity(
    start: datetime, through: datetime, plan: dict
) -> list[tuple[str, datetime, int | None]]:
    unique: dict[tuple[str, str], tuple[datetime, int | None]] = {}
    for repository in REPOSITORIES:
        for pull_number in merged_pr_numbers(repository, start, through):
            step = step_for_pr(repository, pull_number, plan)
            for sha, commit_time in commit_times(repository, pull_number):
                if start <= commit_time <= through:
                    key = (repository, sha)
                    previous = unique.get(key)
                    if previous and previous[1] != step:
                        raise SystemExit(
                            f"Commit {repository}@{sha} maps to multiple SIP steps"
                        )
                    unique[key] = (commit_time, step)
    return sorted(
        (
            (repository, commit_time, step)
            for (repository, _), (commit_time, step) in unique.items()
        ),
        key=lambda item: item[1],
    )


def activity_blocks(
    activity: list[tuple[str, datetime, int | None]],
) -> list[tuple[datetime, datetime, set[str], int]]:
    half_window = timedelta(minutes=WINDOW_MINUTES / 2)
    blocks: list[tuple[datetime, datetime, set[str], int]] = []

    for repository, commit_time, _ in activity:
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


def update_snapshot(
    path: Path,
    through: date,
    project_days: float,
    step_project_days: dict[int, float],
) -> None:
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
    text = text[: actuals.start("body")] + body + text[actuals.end("body") :]

    for step, value in sorted(step_project_days.items()):
        step_match = re.search(
            rf'(?ms)(^  "{step}":\n)(?P<body>.*?)(?=^  "[0-9]+":|\Z)',
            text,
        )
        if not step_match:
            raise SystemExit(f"Could not find SIP Step {step} in {path}")
        step_body = step_match.group("body")
        actual_line = re.search(
            r"(?m)^    actual_estimated_project_days:\s*.*$",
            step_body,
        )
        replacement = f"    actual_estimated_project_days: {value:.1f}"
        if actual_line:
            step_body = (
                step_body[: actual_line.start()]
                + replacement
                + step_body[actual_line.end() :]
            )
        else:
            estimate_line = re.search(
                r"(?m)^    estimate_project_days:\s*.*$",
                step_body,
            )
            if not estimate_line:
                raise SystemExit(f"Missing estimate for SIP Step {step}")
            insert_at = estimate_line.end()
            step_body = (
                step_body[:insert_at]
                + "\n"
                + replacement
                + step_body[insert_at:]
            )
        text = (
            text[: step_match.start("body")]
            + step_body
            + text[step_match.end("body") :]
        )

    path.write_text(text, encoding="utf-8")


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

    activity = collect_activity(start, through, plan)
    blocks = activity_blocks(activity)
    total_hours = sum((end - start).total_seconds() for start, end, _, _ in blocks) / 3600
    project_days = total_hours / PROJECT_DAY_HOURS

    attributed_steps = sorted(
        {step for _, _, step in activity if step is not None}
    )
    step_results: dict[int, tuple[int, int, float, float]] = {}
    for step in attributed_steps:
        step_activity = [item for item in activity if item[2] == step]
        step_blocks = activity_blocks(step_activity)
        step_hours = sum(
            (end - start).total_seconds()
            for start, end, _, _ in step_blocks
        ) / 3600
        step_results[step] = (
            len(step_activity),
            len(step_blocks),
            step_hours,
            step_hours / PROJECT_DAY_HOURS,
        )
    unassigned = sum(1 for _, _, step in activity if step is None)

    print("SIP actual-effort planning indication")
    print(f"Range:        {start_date} through {args.through}")
    print(f"Repositories: {', '.join(REPOSITORIES)}")
    print(f"Commits:      {len(activity)} merged-PR commits")
    print(f"Window:       {WINDOW_MINUTES} min per commit (±{WINDOW_MINUTES / 2:g} min)")
    print(f"Blocks:       {len(blocks)}")
    print(f"Hours:        {total_hours:.2f}")
    print(f"Project days: {project_days:.2f} ({PROJECT_DAY_HOURS:g} h/day)")
    print(f"Unassigned:   {unassigned} commits")
    print()
    print("Per SIP step:")
    for step, (commits, block_count, hours, days) in step_results.items():
        print(
            f"  Step {step:2d}: {days:5.2f}d  {hours:6.2f}h  "
            f"{commits:3d} commits  {block_count:2d} blocks"
        )
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
        rounded_steps = {
            step: round(values[3], 1)
            for step, values in step_results.items()
        }
        update_snapshot(args.plan, args.through, rounded, rounded_steps)
        print()
        print(
            f"Updated {args.plan}: through_date={args.through}, "
            f"estimated_project_days={rounded:.1f}"
        )
        for step, value in rounded_steps.items():
            print(f"  Step {step}: actual_estimated_project_days={value:.1f}")


if __name__ == "__main__":
    main()
