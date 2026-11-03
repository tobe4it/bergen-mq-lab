#!/usr/bin/env python3
"""Validate local documentation links and the structure of translated wiki guides.

Stdlib only, suitable for offline CI. External URLs intentionally are not fetched:
network outages must not block a source-only structural check.
"""
from __future__ import annotations

from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = ("en", "de", "fr")
EXPECTED_SECTIONS = 12
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^## (\d+)\. ", re.MULTILINE)
DOC_SUFFIXES = {".md", ".markdown"}
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__"}
errors: list[str] = []


def check_links(path: Path, text: str) -> None:
    for raw in LINK_RE.findall(text):
        destination = raw.split(maxsplit=1)[0].strip("<>")
        if not destination or destination.startswith(("#", "mailto:")):
            continue
        parsed = urlsplit(destination)
        if parsed.scheme in ("http", "https"):
            continue
        if parsed.scheme or destination.startswith("//"):
            continue
        target = (path.parent / unquote(parsed.path)).resolve()
        if not target.is_relative_to(ROOT.resolve()):
            errors.append(f"{path.relative_to(ROOT)}: link escapes repository: {raw}")
        elif not target.exists():
            errors.append(f"{path.relative_to(ROOT)}: missing local link: {raw}")


def main() -> int:
    paths = sorted(p for p in ROOT.rglob("*.md") if not any(part in SKIP_DIRS for part in p.relative_to(ROOT).parts))
    if not paths:
        errors.append("No Markdown files found")
    for path in paths:
        text = path.read_text(encoding="utf-8")
        if not text.strip() or not text.startswith("# "):
            errors.append(f"{path.relative_to(ROOT)}: document must start with an H1 heading")
        check_links(path, text)

    for lang in LANGUAGES:
        path = ROOT / "wiki" / lang / "Guide.md"
        if not path.is_file():
            errors.append(f"Missing guide: wiki/{lang}/Guide.md")
            continue
        guide = path.read_text(encoding="utf-8")
        sections = [int(number) for number in HEADING_RE.findall(guide)]
        if sections != list(range(1, EXPECTED_SECTIONS + 1)):
            errors.append(f"wiki/{lang}/Guide.md: expected sections 1–{EXPECTED_SECTIONS}, found {sections}")
        for name in ("MQ-LAB.md", "MQ.md", "MQSC-DEPLOY.md", "MQ-AUDIT.md", "MQ-TOPOLOGY.md"):
            if name not in guide:
                errors.append(f"wiki/{lang}/Guide.md: missing reference to {name}")

    for name in ("Home.md", "_Sidebar.md"):
        if not (ROOT / "wiki" / name).is_file():
            errors.append(f"Missing wiki/{name}")

    for error in errors:
        print("ERROR:", error, file=sys.stderr)
    print(f"Documentation files checked: {len(paths)}; language guides: {len(LANGUAGES)}; errors: {len(errors)}")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
