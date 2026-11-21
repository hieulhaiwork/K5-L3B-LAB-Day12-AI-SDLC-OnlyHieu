"""Tạo ZIP nguồn chạy được, chỉ gồm file dự án và hướng dẫn bàn giao."""

import argparse
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = ("README.md", "TEAM.md", "AGENTS.md", "CHANGELOG.md", "CREDITS.md", "LICENSE",
         "RELEASE_NOTES.md", "game.contract.json")
SOURCES = {
    "chonoi": {".py", ".html", ".js"},
    "tests": {".py", ".cjs", ".json", ".jsonl"},
    "tools": {".py", ".cjs"},
    "docs": {".md", ".json", ".png"},
    ".agents/skills": {".md"},
}


def package(destination):
    files = [ROOT / name for name in FILES]
    for directory, suffixes in SOURCES.items():
        files.extend(p for p in (ROOT / directory).rglob("*") if p.is_file() and p.suffix in suffixes)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as output:
        for source in sorted(files):
            relative = source.relative_to(ROOT).as_posix()
            entry = zipfile.ZipInfo(f"mot-ngay-o-cho-noi-v1.0.0/{relative}", (2026, 1, 1, 0, 0, 0))
            output.writestr(entry, source.read_bytes(), compress_type=zipfile.ZIP_DEFLATED)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "dist/mot-ngay-o-cho-noi-v1.0.0.zip")
    args = parser.parse_args()
    package(args.out)
    print(args.out)
