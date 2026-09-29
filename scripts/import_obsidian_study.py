"""Archive nonempty Obsidian study notes as tagged Jekyll posts.

Usage: python3 scripts/import_obsidian_study.py /path/to/vault/study
The existing curated MVCC post represents its source note and is skipped.
"""

from __future__ import annotations

import hashlib
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CURATED_SOURCE = (
    "study plan/Arc1 - Booking System/Part1 - Transaction. MVCC. Lock/"
    "MVCC; Multi Versioning Concurrency Control.md"
)


def section_and_tags(relative: Path) -> tuple[str, list[str]]:
    name = relative.stem.casefold()
    path = str(relative).casefold()
    if "arc1 - booking system" in path:
        section, tags = "database", ["database", "booking-system"]
        if "part1" in path:
            tags.append("concurrency")
        if "part2" in path:
            tags.append("indexes")
    elif "arc2 - api design" in path:
        section, tags = "backend", ["backend", "api-design"]
    elif "roadmap" in path or "checkpoint" in path:
        section, tags = "learning", ["learning", "study-plan"]
    elif "toy project" in path:
        section, tags = "project", ["project", "booking-system"]
    else:
        section, tags = "backend", ["backend"]

    keywords = {
        "mvcc": "mvcc",
        "transaction": "transactions",
        "lock": "locking",
        "deadlock": "deadlocks",
        "atomic": "atomic-update",
        "invariant": "invariants",
        "index": "indexes",
        "query": "queries",
        "jpa": "jpa",
        "redis": "redis",
        "spring": "spring",
        "exception": "exceptions",
        "예외": "exceptions",
    }
    for needle, tag in keywords.items():
        if needle in name and tag not in tags:
            tags.append(tag)
    if "redis" in name:
        section = "database"
        tags = ["database", *[tag for tag in tags if tag != "backend"]]
    return section, tags


def slug_for(relative: Path) -> str:
    normalized = unicodedata.normalize("NFKD", relative.stem)
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii").lower()
    readable = re.sub(r"[^a-z0-9]+", "-", ascii_name).strip("-")[:65]
    digest = hashlib.sha1(str(relative).encode("utf-8")).hexdigest()[:8]
    return f"{readable or 'note'}-{digest}"


def split_front_matter(text: str) -> tuple[str, str]:
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[4:end], text[end + 5 :]
    return "", text


def original_tags(front_matter: str) -> list[str]:
    tags: list[str] = []
    collecting = False
    for line in front_matter.splitlines():
        if line == "tags:":
            collecting = True
        elif collecting and line.startswith("  - "):
            tags.append(line[4:].strip().lower())
        elif collecting and line and not line.startswith(" "):
            collecting = False
    return tags


def quote_yaml(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main(source_root: Path) -> None:
    count = 0
    for source in sorted(source_root.rglob("*.md")):
        relative = source.relative_to(source_root)
        if relative.as_posix() == CURATED_SOURCE:
            continue
        original = source.read_text(encoding="utf-8-sig")
        if not original.strip():
            continue
        front_matter, body = split_front_matter(original)
        section, tags = section_and_tags(relative)
        for tag in original_tags(front_matter):
            if tag not in tags:
                tags.append(tag)
        modified = datetime.fromtimestamp(source.stat().st_mtime, tz=timezone.utc)
        date = modified.strftime("%Y-%m-%d")
        slug = slug_for(relative)
        destination = ROOT / section / "_posts" / f"{date}-{slug}.md"
        destination.parent.mkdir(parents=True, exist_ok=True)
        header = "\n".join(
            [
                "---",
                "layout: post",
                f"title: {quote_yaml(relative.stem)}",
                f"date: {modified.strftime('%Y-%m-%d %H:%M:%S +0000')}",
                f"categories: [{section}]",
                f"tags: [{', '.join(tags)}]",
                f"permalink: /{section}/{slug}/",
                f"source_note: {quote_yaml(relative.as_posix())}",
                "---",
                "",
                f"[{'Projects' if section == 'project' else section.title()}]({{{{ '/%s/' | relative_url }}}}) / Study archive" % ("projects" if section == "project" else section),
                "",
            ]
        )
        destination.write_text(header + body.rstrip() + "\n", encoding="utf-8")
        count += 1
    print(f"Archived {count} source notes")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: import_obsidian_study.py /path/to/vault/study")
    main(Path(sys.argv[1]).expanduser().resolve())
