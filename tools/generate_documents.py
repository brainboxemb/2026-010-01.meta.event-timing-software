#!/usr/bin/env python3
"""Build GitHub-readable generated documentation from source Markdown + diagrams.

The source documents remain authoritative on the normal source branch. This
script creates a review/output document set under bld/docs with local diagram
links, an architecture book, and a combined software document set.
"""

from pathlib import Path
import argparse
import re
import shutil


CONTEXT_DOCUMENTS = [
    "03-domain-baseline.md",
]

PLANNING_DOCUMENTS = [
    "10-SDP-software-development-plan.md",
    "11-SIP-software-implementation-planning.md",
]

EXTERNAL_INPUT_DOCUMENTS = [
    "20-EXT-external-system-inputs.md",
]

SYSTEM_SPEC_DOCUMENTS = [
    "30-UC-system-use-cases.md",
    "31-SSSD-software-system-specification-document.md",
    "32-IDD-03-application-control-status.md",
    "33-IDD-11-application-configuration.md",
]

SOFTWARE_ITEM_SPEC_DOCUMENTS = [
    "41-01-SSD-timing-application-specification-document.md",
    "41-02-SSD-gui-application-specification-document.md",
]

ENGINEERING_DOCUMENTS = [
    "50-SDE-software-development-environment.md",
    "51-SDE-java-build-test-toolchain.md",
]

ARCHITECTURE_DOCUMENTS = [
    "31-SSSD-software-system-specification-document.md",
    "32-IDD-03-application-control-status.md",
    "33-IDD-11-application-configuration.md",
    "41-01-SSD-timing-application-specification-document.md",
    "43-01-SDD-02-java-component-design.md",
    "41-02-SSD-gui-application-specification-document.md",
]

DEFERRED_DESIGN_DOCUMENTS = [
    "43-01-SDD-01-data-and-display-design.md",
    "43-01-SDD-03-backoffice-transport-design.md",
]

VERIFICATION_DOCUMENTS = [
    "60-SVP-software-verification-plan.md",
]

USER_DOCUMENTS = [
    "70-01-SUM-headless-timing-application.md",
]

DOCUMENTS = (
    CONTEXT_DOCUMENTS
    + PLANNING_DOCUMENTS
    + EXTERNAL_INPUT_DOCUMENTS
    + SYSTEM_SPEC_DOCUMENTS
    + SOFTWARE_ITEM_SPEC_DOCUMENTS
    + DEFERRED_DESIGN_DOCUMENTS
    + ["43-01-SDD-02-java-component-design.md"]
    + ENGINEERING_DOCUMENTS
    + VERIFICATION_DOCUMENTS
    + USER_DOCUMENTS
)


RAW_DIAGRAM_LINK = re.compile(
    r"\.\./\.\./\.\./raw/(?:prod/docs|dev/pr-\d+/docs)/(?:assets/)?architecture/([^\s)]+)"
)
BLOB_DIAGRAM_LINK = re.compile(
    r"\.\./\.\./\.\./blob/(?:prod/docs|dev/pr-\d+/docs)/(?:assets/)?architecture/([^\s)]+)"
)


def localise_links(text: str) -> str:
    """Rewrite generated-branch diagram links to local generated assets."""
    text = RAW_DIAGRAM_LINK.sub(r"../assets/architecture/\1", text)
    text = BLOB_DIAGRAM_LINK.sub(r"../assets/architecture/\1", text)
    return text


def read_source(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    return localise_links(text).rstrip() + "\n"


def title_of(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def as_book_section(text: str, title: str, filename: str) -> str:
    """Embed a Markdown document one heading level lower in a combined book."""
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]

    shifted = []
    fenced = False
    for line in lines:
        if line.startswith("```"):
            fenced = not fenced
            shifted.append(line)
            continue
        if not fenced and line.startswith("#"):
            line = "#" + line
        shifted.append(line)

    source_ref = f"**Source document:** [{filename}](./{filename})"
    return (
        "## " + title + "\n\n"
        + source_ref + "\n\n"
        + "\n".join(shifted).strip()
        + "\n"
    )


def write_book(path: Path, title: str, description: str, built) -> None:
    content = [
        f"# {title}",
        "",
        description,
        "",
        "The numbered source documents on the source branch remain authoritative.",
        "",
        "## Contents",
        "",
    ]

    for filename, document_title, _ in built:
        content.append(f"- [{document_title}](./{filename})")

    content.extend(["", "---", ""])

    for filename, document_title, text in built:
        content.append(as_book_section(text, document_title, filename))
        content.append("\n---\n")

    path.write_text("\n".join(content), encoding="utf-8")


def generate(source_dir: Path, diagram_dir: Path, out_dir: Path) -> None:
    documents_dir = out_dir / "documents"
    assets_dir = out_dir / "assets" / "architecture"
    documents_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)

    if not diagram_dir.exists():
        raise SystemExit(f"diagram directory does not exist: {diagram_dir}")

    for path in diagram_dir.iterdir():
        if path.is_file():
            shutil.copy2(path, assets_dir / path.name)

    built = []
    by_name = {}

    for filename in DOCUMENTS:
        source = source_dir / filename
        if not source.exists():
            raise SystemExit(f"missing document source: {source}")

        text = read_source(source)
        title = title_of(text, filename)
        generated = (
            "<!-- Generated review/output copy. Edit the source document on the source branch. -->\n\n"
            + text
        )
        (documents_dir / filename).write_text(generated, encoding="utf-8")
        item = (filename, title, text)
        built.append(item)
        by_name[filename] = item

    architecture_built = [by_name[name] for name in ARCHITECTURE_DOCUMENTS]

    write_book(
        documents_dir / "architecture-book.md",
        "Software architecture document set",
        "Generated review/output book containing the SSSD, system interface contracts, software-item SSDs, and only currently active focused detailed design.",
        architecture_built,
    )

    write_book(
        documents_dir / "software-document-set.md",
        "Software engineering document set",
        "Generated review/output book containing the current context, planning, specifications, interfaces, detailed design and verification documents.",
        built,
    )

    doc_index = [
        "# Generated documents",
        "",
        "## Working context",
        "",
    ]
    for name in CONTEXT_DOCUMENTS:
        _, title, _ = by_name[name]
        doc_index.append(f"- [{title}](./{name})")

    doc_index.extend(["", "## Planning", ""])
    for name in PLANNING_DOCUMENTS:
        _, title, _ = by_name[name]
        doc_index.append(f"- [{title}](./{name})")
    doc_index.append("- [Generated SIP roadmap and printable PDFs](../planning/README.md)")

    doc_index.extend(["", "## External / parent-system inputs", ""])
    for name in EXTERNAL_INPUT_DOCUMENTS:
        _, title, _ = by_name[name]
        doc_index.append(f"- [{title}](./{name})")

    doc_index.extend(["", "## Software-system specification and design", ""])
    for name in SYSTEM_SPEC_DOCUMENTS:
        _, title, _ = by_name[name]
        doc_index.append(f"- [{title}](./{name})")

    doc_index.extend(["", "## Software-item specifications", ""])
    for name in SOFTWARE_ITEM_SPEC_DOCUMENTS:
        _, title, _ = by_name[name]
        doc_index.append(f"- [{title}](./{name})")

    doc_index.extend(["", "## Software-item detailed design — active", ""])
    _, title, _ = by_name["43-01-SDD-02-java-component-design.md"]
    doc_index.append(f"- [{title}](./43-01-SDD-02-java-component-design.md)")

    doc_index.extend(["", "## Software-item detailed design — deferred notes", ""])
    for name in DEFERRED_DESIGN_DOCUMENTS:
        _, title, _ = by_name[name]
        doc_index.append(f"- [{title}](./{name})")

    doc_index.extend(["", "## Development environment / engineering", ""])
    for name in ENGINEERING_DOCUMENTS:
        _, title, _ = by_name[name]
        doc_index.append(f"- [{title}](./{name})")

    doc_index.extend(["", "## Verification and validation", ""])
    for name in VERIFICATION_DOCUMENTS:
        _, title, _ = by_name[name]
        doc_index.append(f"- [{title}](./{name})")

    doc_index.extend(["", "## User / operational documentation", ""])
    for name in USER_DOCUMENTS:
        _, title, _ = by_name[name]
        doc_index.append(f"- [{title}](./{name})")

    doc_index.extend(
        [
            "",
            "## Combined documents",
            "",
            "- [Complete software engineering document set](./software-document-set.md)",
            "- [Architecture book](./architecture-book.md)",
            "",
        ]
    )
    (documents_dir / "README.md").write_text("\n".join(doc_index), encoding="utf-8")

    root_index = [
        "# Generated documentation",
        "",
        "This branch contains generated review/output documentation. Edit source Markdown on the source branch, not here.",
        "",
        "- [Generated document index](documents/README.md)",
        "- [SIP roadmap and printable planning PDFs](planning/README.md)",
        "- [Complete software engineering document set](documents/software-document-set.md)",
        "- [Architecture book](documents/architecture-book.md)",
        "- [Architecture assets](assets/architecture/README.md)",
        "",
    ]
    (out_dir / "README.md").write_text("\n".join(root_index), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="docs")
    parser.add_argument("--diagrams", default="bld/docs/architecture")
    parser.add_argument("--out", default="bld/docs")
    args = parser.parse_args()
    generate(Path(args.source), Path(args.diagrams), Path(args.out))


if __name__ == "__main__":
    main()
