#!/usr/bin/env python3
"""Run cacheable engineering-document producers behind the Moon task boundary.

Project-specific generators remain authoritative. This adapter only gives each
high-level producer a non-overlapping output tree plus retained execution
evidence, then invokes released tool.eng-docs for final assembly.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path.cwd()
PRODUCERS = ROOT / "bld/docs-producers"
TRANSIENT = ROOT / "bld/docs"

TASKS = {
    "diagrams": {
        "task": "docs.diagrams",
        "output": PRODUCERS / "architecture",
        "evidence": PRODUCERS / "evidence/docs-diagrams",
        "commands": [
            ["eng-docs", "diagrams", "--source", "docs/_diagrams", "--theme", "docs/_diagram-theme/default.yaml", "--out", "bld/docs/architecture"],
            [sys.executable, "tools/generate_architecture_diagrams.py"],
            [sys.executable, "tools/generate_timing_detail_diagrams.py"],
            [sys.executable, "tools/generate_data_display_diagrams.py"],
            [sys.executable, "tools/generate_system_model_diagrams.py"],
        ],
    },
    "planning": {
        "task": "docs.planning",
        "output": PRODUCERS / "planning",
        "evidence": PRODUCERS / "evidence/docs-planning",
        "commands": [
            [sys.executable, "tools/generate_sip_planning.py"],
            [sys.executable, "tools/generate_sip_step_pdfs.py"],
            [sys.executable, "tools/generate_sip_manager_roadmap.py"],
        ],
    },
    "assemble": {
        "task": "docs.assemble",
        "output": TRANSIENT,
        "evidence": PRODUCERS / "evidence/docs-assemble",
        "commands": [],
    },
}


def remove(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def git(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=True)
    return result.stdout.strip()


def run_command(argv: list[str], log) -> None:
    rendered = " ".join(argv)
    print(f"> {rendered}")
    log.write(f"\n> {rendered}\n")
    log.flush()
    process = subprocess.Popen(
        argv,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    assert process.stdout is not None
    for line in process.stdout:
        print(line, end="")
        log.write(line)
    code = process.wait()
    log.flush()
    if code:
        raise RuntimeError(f"command failed ({code}): {rendered}")


def validate_diagrams(root: Path) -> dict:
    required = [
        root / "system-overview.svg",
        root / "system-overview.drawio",
        root / "layered-architecture.svg",
        root / "runtime-dispatch-process.svg",
    ]
    for path in required:
        if not path.is_file():
            raise RuntimeError(f"required diagram output missing: {path}")
    for path in sorted(root.glob("*.drawio")) + sorted(root.glob("*.svg")):
        ET.parse(path)
    return {"file_count": sum(path.is_file() for path in root.iterdir())}


def valid_pdf(path: Path) -> None:
    data = path.read_bytes()
    if not data.startswith(b"%PDF-") or b"%%EOF" not in data[-2048:]:
        raise RuntimeError(f"invalid PDF: {path}")


def validate_planning(root: Path) -> dict:
    required = [
        root / "README.md",
        root / "sip-roadmap.svg",
        root / "sip-roadmap.pdf",
        root / "roadmap/sip-roadmap-1.svg",
        root / "roadmap/sip-roadmap-4.svg",
        root / "steps/step-02.svg",
        root / "steps/step-02.pdf",
    ]
    for path in required:
        if not path.is_file():
            raise RuntimeError(f"required planning output missing: {path}")
    ET.parse(root / "sip-roadmap.svg")
    for path in sorted((root / "roadmap").glob("*.svg")):
        ET.parse(path)
    for path in sorted((root / "steps").glob("*.svg")):
        ET.parse(path)
    valid_pdf(root / "sip-roadmap.pdf")
    for path in sorted((root / "steps").glob("*.pdf")):
        valid_pdf(path)
    return {"file_count": sum(path.is_file() for path in root.rglob("*"))}


def validate_assembly(root: Path) -> dict:
    required = [
        root / "README.md",
        root / "documents/README.md",
        root / "documents/software-document-set.md",
        root / "documents/architecture-book.md",
        root / "documents/12-SDE-software-development-environment.md",
        root / "documents/13-SDE-java-build-test-toolchain.md",
        root / "documents/31-01-SAD-timing-application-architecture.md",
        root / "documents/31-01-SDD-02-java-component-design.md",
        root / "documents/50-SVP-software-verification-plan.md",
        root / "assets/architecture/system-overview.svg",
        root / "assets/architecture/system-overview.drawio",
        root / "planning/sip-roadmap.pdf",
    ]
    for path in required:
        if not path.is_file():
            raise RuntimeError(f"required assembled output missing: {path}")
    architecture_book = (root / "documents/architecture-book.md").read_text(encoding="utf-8")
    active = "**Source document:** [31-01-SDD-02-java-component-design.md]"
    deferred = [
        "**Source document:** [31-01-SDD-01-data-and-display-design.md]",
        "**Source document:** [31-01-SDD-03-backoffice-transport-design.md]",
    ]
    if active not in architecture_book:
        raise RuntimeError("active SDD section missing from architecture book")
    if any(marker in architecture_book for marker in deferred):
        raise RuntimeError("deferred SDD section unexpectedly present in architecture book")
    return {
        "document_count": sum(path.is_file() for path in (root / "documents").glob("*.md")),
        "asset_count": sum(path.is_file() for path in (root / "assets/architecture").iterdir()),
    }


def tool_revision() -> str:
    path = ROOT / "tools/tool.eng-docs"
    try:
        return subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"


def producer_revision(name: str) -> str:
    path = PRODUCERS / "evidence" / name / "execution.json"
    if not path.is_file():
        raise RuntimeError(f"producer evidence is missing: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("status") != "success" or not data.get("source_sha"):
        raise RuntimeError(f"producer evidence is incomplete: {path}")
    return str(data["source_sha"])


def prepare_assembly(log) -> None:
    architecture = PRODUCERS / "architecture"
    planning = PRODUCERS / "planning"
    if not architecture.is_dir() or not planning.is_dir():
        raise RuntimeError("documentation producer outputs are missing")

    architecture_revision = producer_revision("docs-diagrams")
    planning_revision = producer_revision("docs-planning")
    assembly_revision = git("rev-parse", "HEAD")
    commands = [
        ["eng-docs", "manifest", "--source", str(architecture.relative_to(ROOT)), "--out", str((architecture / "assets-publication.yml").relative_to(ROOT)), "--producer", "event-timing-software.architecture-publication", "--source-revision", architecture_revision, "--lifecycle", "docs", "--relationship", "producer-source", "--include", "*.svg", "--include", "*.drawio", "--include", "README.md"],
        ["eng-docs", "manifest", "--source", str(architecture.relative_to(ROOT)), "--out", str((architecture / "assets-raw.yml").relative_to(ROOT)), "--producer", "event-timing-software.architecture-raw", "--source-revision", architecture_revision, "--lifecycle", "docs", "--relationship", "producer-source", "--include", "*.svg", "--include", "*.drawio", "--include", "README.md"],
        ["eng-docs", "manifest", "--source", str(planning.relative_to(ROOT)), "--out", str((planning / "assets.yml").relative_to(ROOT)), "--producer", "event-timing-software.planning", "--source-revision", planning_revision, "--lifecycle", "docs", "--relationship", "producer-source"],
        ["eng-docs", "assemble", "--root", ".", "--config", "docs/assembly.yml", "--out", "bld/docs", "--source-repository", "brainboxemb/2026-010-01.meta.event-timing-software", "--source-revision", assembly_revision],
    ]
    for command in commands:
        run_command(command, log)


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in TASKS:
        raise SystemExit("usage: run_docs_task.py diagrams|planning|assemble")

    kind = sys.argv[1]
    cfg = TASKS[kind]
    output: Path = cfg["output"]
    evidence: Path = cfg["evidence"]
    remove(evidence)
    evidence.mkdir(parents=True, exist_ok=True)
    log_path = evidence / "execution.log"
    json_path = evidence / "execution.json"

    source_sha = git("rev-parse", "HEAD")
    task_hash = os.environ.get("MOON_TASK_HASH", "")
    status = "success"
    error = ""
    details: dict = {}

    with log_path.open("w", encoding="utf-8") as log:
        for line in [
            f"Documentation task: {cfg['task']}",
            f"source_sha={source_sha}",
            f"tool_eng_docs_sha={tool_revision()}",
            f"moon_task_hash={task_hash}",
        ]:
            print(line)
            log.write(line + "\n")
        try:
            if kind in ("diagrams", "planning"):
                transient = TRANSIENT / ("architecture" if kind == "diagrams" else "planning")
                remove(transient)
                remove(output)
                TRANSIENT.mkdir(parents=True, exist_ok=True)
                for command in cfg["commands"]:
                    run_command(command, log)
                output.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(transient), str(output))
                details = validate_diagrams(output) if kind == "diagrams" else validate_planning(output)
            else:
                remove(TRANSIENT)
                prepare_assembly(log)
                details = validate_assembly(TRANSIENT)
        except Exception as exc:  # retain useful evidence on producer failures
            status = "failed"
            error = str(exc)
            print(f"ERROR: {error}")
            log.write(f"\nERROR: {error}\n")

    payload = {
        "schema": "event-timing-software.docs-task-evidence",
        "schema_version": 1,
        "task": cfg["task"],
        "status": status,
        "source_sha": source_sha,
        "tool_eng_docs_sha": tool_revision(),
        "moon_task_hash": task_hash,
        "log": "execution.log",
        "details": details,
    }
    if error:
        payload["error"] = error
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    if kind == "assemble" and status == "success":
        (TRANSIENT / "source-sha.txt").write_text(source_sha + "\n", encoding="utf-8")
        target = TRANSIENT / "evidence/tasks"
        target.mkdir(parents=True, exist_ok=True)
        for name in ("docs-diagrams", "docs-planning", "docs-assemble"):
            source = PRODUCERS / "evidence" / name
            if source.is_dir():
                shutil.copytree(source, target / name, dirs_exist_ok=True)

    if status != "success":
        raise SystemExit(error or "documentation task failed")


if __name__ == "__main__":
    main()
