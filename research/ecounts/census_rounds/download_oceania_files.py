#!/usr/bin/env python3
"""Download and flatten all files from the eCounts Oceania folder."""
import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, unquote
from urllib.request import Request, urlopen

BASE_URL = "https://www.databums.org/projects/research/ecounts/census_rounds/2020/oceania/"
USER_AGENT = "Mozilla/5.0 (eCounts Oceania downloader)"


def fetch(url):
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=60) as response:
        return response.read()


def get_links(html, base_url):
    text = html.decode("utf-8", errors="replace")
    links = re.findall(r'href=["\']([^"\']+)["\']', text, flags=re.I)
    results = []
    for link in links:
        link = unquote(link)
        if link in ("../", "./") or link.startswith("#"):
            continue
        full_url = urljoin(base_url, link)
        if full_url.startswith(BASE_URL):
            results.append((link, full_url))
    return results


def safe_filename(url):
    name = unquote(url).split("?")[0].split("#")[0]
    return Path(name).name or "downloaded_file"


def unique_path(output_dir, filename):
    path = output_dir / filename
    if not path.exists():
        return path
    stem, suffix = path.stem, path.suffix
    n = 2
    while True:
        candidate = output_dir / f"{stem}__{n}{suffix}"
        if not candidate.exists():
            return candidate
        n += 1


def discover_files(url, visited=None):
    if visited is None:
        visited = set()
    if url in visited:
        return []
    visited.add(url)
    try:
        html = fetch(url)
    except Exception as exc:
        print(f"[WARN] Could not read {url}: {exc}", file=sys.stderr)
        return []

    files = []
    for link, full_url in get_links(html, url):
        if link.endswith("/"):
            files.extend(discover_files(full_url, visited))
        else:
            files.append(full_url)
    return files


def main():
    parser = argparse.ArgumentParser(description="Download and flatten eCounts Oceania files.")
    parser.add_argument("--output", default=None, help="Output directory; defaults to ./Oceania_All_Files")
    args = parser.parse_args()
    output_dir = Path(args.output).expanduser().resolve() if args.output else Path.cwd() / "Oceania_All_Files"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Reading eCounts Oceania directory...")
    urls = list(dict.fromkeys(discover_files(BASE_URL)))
    if not urls:
        print("No files were found.")
        sys.exit(1)

    print(f"Found {len(urls)} files.")
    print(f"Downloading into: {output_dir}\n")
    downloaded = failed = 0

    for i, url in enumerate(urls, 1):
        filename = safe_filename(url)
        destination = unique_path(output_dir, filename)
        print(f"[{i}/{len(urls)}] {filename}")
        try:
            destination.write_bytes(fetch(url))
            downloaded += 1
        except Exception as exc:
            failed += 1
            print(f"       [FAIL] {exc}", file=sys.stderr)

    print("\nDone.")
    print(f"Downloaded: {downloaded}")
    print(f"Failed:     {failed}")
    print(f"Output:     {output_dir}")


if __name__ == "__main__":
    main()
