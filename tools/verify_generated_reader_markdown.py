#!/usr/bin/env python3
"""Verify generated human-reader Markdown from Sphinx-Needs output."""

from pathlib import Path

root = Path("bld/docs/documents")
text = "\n".join(
    path.read_text(encoding="utf-8")
    for path in sorted(root.rglob("*.md"))
)

forbidden = (
    "```{uc}",
    "```{req}",
    "```{ifreq}",
    "```{arch}",
    "```{vc}",
    ":::{uc}",
    ":::{req}",
    ":::{ifreq}",
    ":::{arch}",
    ":::{vc}",
)
for token in forbidden:
    if token in text:
        raise SystemExit(f"generated reader Markdown still contains {token}")

required = (
    '**SI01-REQ-003 — Configured TimingNode availability**',
    '— — —',
    '- **Type:** Requirement',
    '- **Status:** Review',
    '- **Derived from:**',
    '- **Satisfied by:**',
    '- **Verified by:**',
    '<a id="SI01-REQ-003"></a>',
)
for token in required:
    if token not in text:
        raise SystemExit(f"generated reader Markdown missing {token}")

ssd = (root / "41-01-SSD-timing-application-specification-document.md").read_text(
    encoding="utf-8"
)
start = ssd.index('<a id="SI01-REQ-003"></a>')
end = ssd.index('<a id="SI01-REQ-010"></a>', start)
block = ssd[start:end]
body_text = "SI-01 shall support configuration of one or more"
order = (
    block.index("**SI01-REQ-003 — Configured TimingNode availability**"),
    block.index(body_text),
    block.index("— — —"),
    block.index("- **Type:** Requirement"),
    block.index("- **Derived from:**"),
    block.index("- **Satisfied by:**"),
    block.index("- **Verified by:**"),
    block.index("\n---\n"),
)
if order != tuple(sorted(order)):
    raise SystemExit(
        "generated reader Markdown does not render Need body before metadata/separator"
    )

use_cases = (root / "30-UC-system-use-cases.md").read_text(
    encoding="utf-8"
)
uc_start = use_cases.index('<a id="UC-001"></a>')
uc_end = use_cases.index('<a id="UC-002"></a>', uc_start)
uc_block = use_cases[uc_start:uc_end]
uc_order = (
    uc_block.index("**UC-001 — Connect to a registration system**"),
    uc_block.index("**Preconditions:**"),
    uc_block.index("**Main flow:**"),
    uc_block.index("**Alternative/failure flows:**"),
    uc_block.index("— — —"),
    uc_block.index("- **Type:** Use Case"),
    uc_block.index("\n---\n"),
)
if uc_order != tuple(sorted(uc_order)):
    raise SystemExit(
        "generated reader Markdown does not retain full UC-001 narrative before metadata"
    )

for number in range(1, 20):
    object_id = f"UC-{number:03d}"
    if f'<a id="{object_id}"></a>' not in use_cases:
        raise SystemExit(f"generated reader Markdown missing {object_id}")

si01_ids = (
    "SI01-REQ-001", "SI01-REQ-002", "SI01-REQ-003",
    "SI01-REQ-010", "SI01-REQ-011",
    "SI01-REQ-020", "SI01-REQ-021", "SI01-REQ-022", "SI01-REQ-023",
    "SI01-REQ-030", "SI01-REQ-031", "SI01-REQ-032", "SI01-REQ-033",
    "SI01-REQ-040", "SI01-REQ-041", "SI01-REQ-042", "SI01-REQ-043",
    "SI01-REQ-044", "SI01-REQ-045", "SI01-REQ-046", "SI01-REQ-047",
    "SI01-REQ-048", "SI01-REQ-049", "SI01-REQ-050", "SI01-REQ-051",
    "SI01-REQ-052", "SI01-REQ-053", "SI01-REQ-054",
)
for object_id in si01_ids:
    if f'<a id="{object_id}"></a>' not in ssd:
        raise SystemExit(f"generated reader Markdown missing {object_id}")

isd = (root / "32-03-ISD-application-control-status.md").read_text(
    encoding="utf-8"
)
for number in range(1, 17):
    object_id = f"IF03-REQ-{number:03d}"
    if f'<a id="{object_id}"></a>' not in isd:
        raise SystemExit(f"generated reader Markdown missing {object_id}")

timingdata_isd = (root / "32-05-ISD-timingdata-interchange.md").read_text(
    encoding="utf-8"
)
for number in range(1, 8):
    object_id = f"IF05-REQ-{number:03d}"
    if f'<a id="{object_id}"></a>' not in timingdata_isd:
        raise SystemExit(f"generated reader Markdown missing {object_id}")

if "- **Status:** Draft" not in timingdata_isd:
    raise SystemExit("generated reader Markdown does not expand D to Draft")
if "- **Status:** Review" not in isd:
    raise SystemExit("generated reader Markdown does not expand R to Review")

