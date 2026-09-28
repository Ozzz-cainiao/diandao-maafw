#!/usr/bin/env python3
"""Fetch only pinned dependencies; verify bytes against the committed lockfile."""
import hashlib
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    lock = json.loads((ROOT / 'dependencies.lock.json').read_text())
    for item in lock['files']:
        dest = ROOT / item['path']
        if dest.is_file() and hashlib.sha256(dest.read_bytes()).hexdigest() == item['sha256']:
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(item['url'], timeout=120) as response:
            data = response.read()
        if hashlib.sha256(data).hexdigest() != item['sha256']:
            raise RuntimeError(f"Checksum mismatch: {dest}")
        dest.write_bytes(data)
        print(f"Fetched {item['path']}")

if __name__ == '__main__':
    main()
