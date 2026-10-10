#!/usr/bin/env python3
"""Verify that the generated reader Markdown preserves authored Need content.

This checks rendering behaviour (metadata, body order, links, status labels)
using a few representative objects. Object inventories/relations are *not*
specified here: their authority is the source Needs and the normalized graph,
which validate_engineering_coverage.py checks separately.
Input: bld/docs/documents and, for dynamic ID checks, authored docs/*.md.
"""

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
    "```{design}",
    "```{vc}",
    ":::{uc}",
    ":::{req}",
    ":::{ifreq}",
    ":::{arch}",
    ":::{design}",
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
    '- **Specifies:**',
    '- **Realized by:**',
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
    block.index("- **Specifies:**"),
    block.index("- **Realized by:**"),
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
    uc_block.index("**UC-001 —"),
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

vts = (
    root / "61-01-VTS-timing-application-verification-test-specification.md"
).read_text(encoding="utf-8")
vc_start = vts.index('<a id="VC-ST1-002"></a>')
vc_end = vts.index('<a id="VC-ST1-003"></a>', vc_start)
vc_block = vts[vc_start:vc_end]
vc_order = (
    vc_block.index("**VC-ST1-002 — Control and observe first committed registration**"),
    vc_block.index("- **Type:** Verification Case"),
    vc_block.index("- **Verifies:**"),
    vc_block.index("— — —"),
    vc_block.index("**Executable test**"),
    vc_block.index("**Purpose**"),
    vc_block.index("\n---\n"),
)
if vc_order != tuple(sorted(vc_order)):
    raise SystemExit(
        "generated reader Markdown does not render VC metadata before testcase body"
    )

sdd = (root / "43-01-SDD-02-java-component-design.md").read_text(
    encoding="utf-8"
)
if '<a id="DD-PresentationAccess"></a>' not in sdd:
    raise SystemExit("generated reader Markdown missing DD-PresentationAccess")
if "- **Type:** Detailed Design" not in sdd:
    raise SystemExit("generated reader Markdown missing Detailed Design type label")
if "Node-scoped presentation access is exposed through `TimingNodeProxy`." not in sdd:
    raise SystemExit(
        "generated reader Markdown missing substantive DD-PresentationAccess body"
    )

presentation_start = ssd.index('<a id="PresentationGateway"></a>')
presentation_end = ssd.index('<a id="TimingNodeProxy"></a>', presentation_start)
presentation_block = ssd[presentation_start:presentation_end]
if "- **Elaborated by:**" not in presentation_block:
    raise SystemExit("generated reader Markdown missing incoming elaborates relation")
if "DD-PresentationAccess" not in presentation_block:
    raise SystemExit("generated reader Markdown does not link PresentationGateway to DD-PresentationAccess")

design_start = sdd.index('<a id="DD-PresentationAccess"></a>')
design_end = sdd.index("\n---\n", design_start)
design_block = sdd[design_start:design_end]
if "- **Elaborates:**" not in design_block:
    raise SystemExit("generated reader Markdown missing outgoing elaborates relation")
if "PresentationGateway" not in design_block or "TimingNodeProxy" not in design_block:
    raise SystemExit("generated reader Markdown missing inverse SSD architecture links")

# Verify all current source Need IDs survived reader generation. Unlike a
# hard-coded range/list, this automatically tracks future UC/REQ additions.
import re

# Check the same project-wide readable Need header format for VTS cases.
# The test discovers cases from source instead of duplicating a list of VC IDs.
vts_source = Path(
    "docs/61-01-VTS-timing-application-verification-test-specification.md"
).read_text(encoding="utf-8")
vc_headers = re.findall(
    r"(?m)^(:::\{vc\}[^\n]*\n:id: VC-[^\n]*\n:verifies:[^\n]*)\n",
    vts_source,
)
vts_case_count = len(re.findall(r"(?m)^:::\{vc\}", vts_source))
if not vc_headers or len(vc_headers) != vts_case_count:
    raise SystemExit("VTS cases must use :id: and :verifies: Need options")
for vc_header in vc_headers:
    if any(not line.endswith("  ") for line in vc_header.splitlines()):
        raise SystemExit("VTS Need header lines must end with two spaces")

sources = {
    "30-UC-system-use-cases.md": "uc",
    "41-01-SSD-timing-application-specification-document.md": "req",
    "41-02-SSD-gui-application-specification-document.md": "req",
    "32-03-ISD-application-control-status.md": "ifreq",
    "32-05-ISD-timingdata-interchange.md": "ifreq",
    "61-01-VTS-timing-application-verification-test-specification.md": "vc",
}
for filename, need_type in sources.items():
    authored = (Path("docs") / filename).read_text(encoding="utf-8")
    output = (root / filename).read_text(encoding="utf-8")
    source_ids = set(
        re.findall(
            rf"(?m)^:::\{{{need_type}\}}[^\n]*\n:id: ([A-Za-z0-9_-]+)",
            authored,
        )
    )
    if not source_ids:
        raise SystemExit(f"no authored {need_type} objects in {filename}")
    missing = sorted(
        need_id
        for need_id in source_ids
        if f'<a id="{need_id}"></a>' not in output
    )
    if missing:
        raise SystemExit(f"reader Markdown lost source Needs from {filename}: {missing}")

isd = (root / "32-03-ISD-application-control-status.md").read_text(encoding="utf-8")
timingdata_isd = (root / "32-05-ISD-timingdata-interchange.md").read_text(encoding="utf-8")
if "- **Status:** Draft" not in timingdata_isd:
    raise SystemExit("generated reader Markdown does not expand D to Draft")
if "- **Status:** Review" not in isd:
    raise SystemExit("generated reader Markdown does not expand R to Review")

