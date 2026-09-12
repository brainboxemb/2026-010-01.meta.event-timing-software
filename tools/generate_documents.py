#!/usr/bin/env python3
"""Build GitHub-readable generated documentation from source Markdown + diagrams.

The source documents remain authoritative on the normal source branch. This
script creates a review/output document set under bld/docs with local diagram
links, plus a combined architecture book.
"""

from pathlib import Path
import argparse
import re
import shutil


DOCUMENTS = [
    "30-SSAD-software-system-architecture.md",
    "31-01-SAD-timing-application-architecture.md",
    "31-02-SDD-timing-system-detailed-design.md",
    "31-03-SDD-data-and-display-design.md",
    "31-04-SDD-java-component-design.md",
]


RAW_DIAGRAM_LINK = re.compile(
    r"\.\./\.\./\.\./raw/(?:prod/docs|dev/pr-\d+/docs)/architecture/([^\s)]+)"
)
BLOB_DIAGRAM_LINK = re.compile(
    r"\.\./\.\./\.\./blob/(?:prod/docs|dev/pr-\d+/docs)/architecture/([^\s)]+)"
)


def localise_links(text: str) -> str:
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


def as_book_section(text: str, title: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    shifted = []
    for line in lines:
        if line.startswith("#"):
            line = "#" + line
        shifted.append(line)
    return "## " + title + "\n\n" + "\n".join(shifted).strip() + "\n"


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
        built.append((filename, title, text))

    book = [
        "# Software architecture document set",
        "",
        "Generated review/output document. The numbered source documents remain authoritative.",
        "",
        "## Contents",
        "",
    ]
    for filename, title, _ in built:
        book.append(f"- [{title}](./{filename})")
    book.append("")
    book.append("---")
    book.append("")
    for _, title, text in built:
        book.append(as_book_section(text, title))
        book.append("\n---\n")
    (documents_dir / "architecture-book.md").write_text("\n".join(book), encoding="utf-8")

    doc_index = ["# Generated documents", ""]
    for filename, title, _ in built:
        doc_index.append(f"- [{title}](./{filename})")
    doc_index.extend(["", "- [Combined architecture book](./architecture-book.md)", ""])
    (documents_dir / "README.md").write_text("\n".join(doc_index), encoding="utf-8")

    root_index = [
        "# Generated documentation",
        "",
        "This branch contains generated review/output documentation. Edit source Markdown on the source branch, not here.",
        "",
        "- [Generated document set](documents/README.md)",
        "- [Combined architecture book](documents/architecture-book.md)",
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
