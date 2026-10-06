# bWAPP Kali Installation Guide

A practical guide to installing [lmoroz/bWAPP](https://github.com/lmoroz/bWAPP) on Kali Linux with Docker, including the Debian Bullseye security repository 404 repair confirmed on 6 October 2026.

**Author:** Rajsegar Alagarathnam  
**Application installation:** confirmed working by the author in the recorded session  
**Scope:** local training lab installation, configuration, and troubleshooting  
**Repository:** https://github.com/rajsegar/bwapp-kali-installation-guide

## Files

| File | Purpose |
|---|---|
| docs/installation-report.md | Full setup, diagnosis, evidence, and troubleshooting |
| docs/BWAPP_Kali_Installation_Notes.pdf | Printable installation guide and restart commands |
| docs/medium-article.md | Ready-to-edit Medium article draft |
| docs/quick-reference.md | Next-session commands |
| compose.local.yml | Local web binding and internal MySQL service |
| scripts/patch-bullseye-security.py | Repeat-safe Dockerfile archive repair |

This repository contains original notes and helper configuration. The bWAPP application is downloaded separately from its upstream project; its source is not vendored here.

## Fresh install

Start with the package installation and upstream clone below:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose git python3
sudo systemctl start docker
sudo docker compose version
```
```bash
mkdir -p ~/Desktop/labs
cd ~/Desktop/labs
git clone https://github.com/lmoroz/bWAPP.git
cd bWAPP
```

From this guide repository, copy compose.local.yml into the upstream bWAPP folder. Run scripts/patch-bullseye-security.py with the upstream bWAPP folder as the current directory. For a standalone copy-and-paste route, the report includes both file contents and an inline Python patch block.

```bash
sudo docker compose -f compose.local.yml build --no-cache web
sudo docker compose -f compose.local.yml up -d
sudo docker compose -f compose.local.yml ps
```

Open http://127.0.0.1:8080/bWAPP/install.php in Kali's browser and click “here”. Then open http://127.0.0.1:8080/bWAPP/login.php and use bee / bug.

## Restart and stop

```bash
cd ~/Desktop/labs/bWAPP
sudo systemctl start docker
sudo docker compose -f compose.local.yml up -d
```
```bash
sudo docker compose -f compose.local.yml stop
```

## Why the patch exists

The upstream image uses PHP 7.4 on Debian Bullseye. The supplied build log showed security package download 404s after apt-get update completed. The fix points that security source at Debian's archive and permits archived index metadata without disabling signature verification. It does not change Kali's APT repositories.

The patch checks for the known upstream install line, preserves an existing backup, and does not patch a previously fixed file twice. This configuration binds the web port to 127.0.0.1 and does not publish MySQL's port. Legacy image availability and future upstream changes can affect fresh installs.

## Validation

The installation outcome comes from the recorded terminal log and the user's confirmation. Patch-helper checks cover applying the transformation, an unchanged repeat run, preserving the backup, and rejecting an unexpected Dockerfile. No fresh Docker build was run by the document generator.

## Attribution and references

bWAPP was created by Malik Mesellem. This guide uses Larisa Moroz's Docker repository as the installation source. The upstream application retains its own licensing; these notes do not relicense it.

- [Upstream repository and setup](https://github.com/lmoroz/bWAPP/tree/master)
- [Upstream Dockerfile](https://github.com/lmoroz/bWAPP/blob/master/Dockerfile)
- [Upstream installation / credentials](https://github.com/lmoroz/bWAPP/blob/master/INSTALL.txt)
- [Installing Docker on Kali](https://www.kali.org/docs/containers/installing-docker-on-kali/)
- [Debian Bullseye LTS end of life](https://www.debian.org/News/2026/20260831)
- [Debian archive transition, bug 1147093](https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1147093)
- [Docker build best practices](https://docs.docker.com/build/building/best-practices/)
