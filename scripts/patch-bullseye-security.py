#!/usr/bin/env python3
"""Repair the recorded bWAPP Bullseye security package source."""
from pathlib import Path

path = Path("Dockerfile")
text = path.read_text()
old = "RUN apt-get update && apt-get install -y iputils-ping dnsutils"
new = (
    'RUN sed -i '
    '"s|http://deb.debian.org/debian-security|'
    'https://archive.debian.org/debian-security|g" '
    '/etc/apt/sources.list && rm -rf /var/lib/apt/lists/*\n'
    'RUN apt-get -o Acquire::Check-Valid-Until=false update '
    '&& apt-get install -y iputils-ping dnsutils'
)
if "archive.debian.org/debian-security" in text and (
    "Acquire::Check-Valid-Until=false" in text
):
    print("Archive fix already present; Dockerfile unchanged.")
elif old in text:
    backup = path.with_name("Dockerfile.before-fix")
    if not backup.exists():
        backup.write_text(text)
    path.write_text(text.replace(old, new, 1))
    print("Dockerfile patched; original backup preserved.")
else:
    raise SystemExit("Dockerfile differs: review before applying this fix.")
