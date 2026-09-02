#!/usr/bin/env python3

from pathlib import Path
import shutil
import sys

BASE = Path(
    "/Users/vthompson/Documents/github/vic3347.github.io/"
    "projects/research/ecounts/census_rounds/2020"
)

POSSIBLE_NAMES = [
    "South_America",
    "South America",
    "South-America",
    "south_america",
    "south america",
]

OUTPUT_NAME = "/Users/vthompson/Downloads/South_America_All_Files"


def find_south_america_folder(base: Path) -> Path:
    for name in POSSIBLE_NAMES:
        candidate = base / name
        if candidate.is_dir():
            return candidate

    matches = []
    for p in base.rglob("*"):
        if p.is_dir() and p.name.lower().replace("-", "_").replace(" ", "_") == "south_america":
            matches.append(p)

    if len(matches) == 1:
        return matches[0]

    if len(matches) > 1:
        print("More than one possible South America folder was found:")
        for p in matches:
            print(f"  {p}")
        sys.exit("\nPlease edit the script and set the correct folder name.")

    sys.exit(
        f"Could not find a South America folder beneath:\n{base}\n"
        "Check the directory name and edit POSSIBLE_NAMES if necessary."
    )


def unique_destination(output_dir: Path, source_file: Path) -> Path:
    dest = output_dir / source_file.name
    if not dest.exists():
        return dest

    stem = source_file.stem
    suffix = source_file.suffix
    n = 2

    while True:
        dest = output_dir / f"{stem}__{n}{suffix}"
        if not dest.exists():
            return dest
        n += 1


def main():
    if not BASE.is_dir():
        sys.exit(f"Base directory does not exist:\n{BASE}")

    south_america = find_south_america_folder(BASE)

    output_dir = south_america.parent / OUTPUT_NAME
    output_dir.mkdir(parents=True, exist_ok=True)

    files = [
        p for p in south_america.rglob("*")
        if p.is_file() and output_dir not in p.parents
    ]

    if not files:
        sys.exit(f"No files found beneath:\n{south_america}")

    copied = 0
    renamed = 0

    print(f"Source:      {south_america}")
    print(f"Destination: {output_dir}")
    print(f"Files found: {len(files)}\n")

    for src in sorted(files):
        dest = unique_destination(output_dir, src)

        if dest.name != src.name:
            renamed += 1

        shutil.copy2(src, dest)
        copied += 1
        print(f"[{copied}/{len(files)}] {src.relative_to(south_america)}")
        print(f"    -> {dest.name}")

    print("\nDone.")
    print(f"Copied: {copied} files")
    print(f"Renamed because of duplicate filenames: {renamed}")
    print(f"Flattened folder:\n{output_dir}")


if __name__ == "__main__":
    main()
