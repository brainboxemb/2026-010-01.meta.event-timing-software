#!/usr/bin/env python3
"""Compare qualification docs output with the current production publication."""

from __future__ import annotations

from pathlib import Path
import argparse


def file_set(root: Path) -> set[str]:
    return {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--candidate", required=True)
    args = parser.parse_args()

    baseline = Path(args.baseline)
    candidate = Path(args.candidate)

    baseline_files = file_set(baseline) - {"source-sha.txt"}
    candidate_files = {
        path for path in file_set(candidate)
        if not path.startswith("_manifests/") and path != "source-sha.txt"
    }

    missing = sorted(baseline_files - candidate_files)
    extra = sorted(candidate_files - baseline_files)
    if missing or extra:
        if missing:
            print("Missing files relative to prod/docs:")
            for path in missing:
                print(f"  - {path}")
        if extra:
            print("Unexpected files relative to prod/docs:")
            for path in extra:
                print(f"  + {path}")
        raise SystemExit("generated documentation file set differs from prod/docs")

    checked = 0
    for relative in sorted(baseline_files):
        if not relative.endswith((".svg", ".drawio")):
            continue
        expected = (baseline / relative).read_bytes()
        actual = (candidate / relative).read_bytes()
        if actual != expected:
            raise SystemExit(f"producer output differs from prod/docs: {relative}")
        checked += 1

    print(
        f"Publication qualification passed: {len(baseline_files)} legacy files preserved, "
        f"{checked} SVG/draw.io producer outputs byte-identical; new _manifests/ provenance allowed."
    )


if __name__ == "__main__":
    main()
