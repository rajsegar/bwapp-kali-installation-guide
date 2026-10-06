# bWAPP on Kali Linux: Installation Report

**Prepared for:** Rajsegar Alagarathnam  
**Installation confirmed:** 6 October 2026, Europe/London  
**Status:** Working installation confirmed by the user  
**Purpose:** Reusable installation notes for a local web security training lab

## 1. Outcome and evidence

bWAPP was installed on Kali using the lmoroz/bWAPP Docker configuration, with a separate local Compose file. The first web image build failed while downloading Debian Bullseye security packages. After pointing the security package source to Debian's archive and rebuilding, the user confirmed that the application worked.

The evidence is the terminal build output supplied in this conversation and the user's confirmation. This report does not claim an independent connection to the user's Kali computer or invent container IDs, screenshots, or exact host versions.

## 2. Components and configuration

| Component | Recorded configuration | Role |
|---|---|---|
| Host | Kali Linux; release not supplied | Runs Docker and the browser |
| Working folder | ~/Desktop/labs/bWAPP | Upstream checkout and local configuration |
| Web image base | php:7.4-apache | Apache and PHP runtime |
| Container OS in the supplied log | Debian 11 Bullseye, amd64 | Package source affected by the failure |
| Database image | mysql:5.7 | bWAPP database |
| Web address | http://127.0.0.1:8080/bWAPP/ | Access from Kali's browser |
| Port mapping | 127.0.0.1:8080:80 | Kali port 8080 to container port 80 |
| Database networking | Compose service name db; internal port 3306 | Web-to-database connection |
| Persistence | db_data:/var/lib/mysql | Retains database data across container recreation |
| Default application account | bee / bug | Initial bWAPP login |

The upstream settings.php already uses database host db, user root, and an empty password. No host database installation is required. The MySQL port is not published on the host. The browser URLs apply inside Kali; a Windows or macOS browser outside the Kali VM has a different localhost.

## 3. Requirements and package installation

Use a Kali desktop or VM with working networking and sudo access. The original log used amd64; the old mysql:5.7 image may not have a native ARM image. Internet access is needed for APT, GitHub, and Docker image downloads.

```bash
sudo apt update
sudo apt install -y docker.io docker-compose git python3
sudo systemctl start docker
sudo docker compose version
```

If the installed Compose command is available only as docker-compose, substitute that command for docker compose throughout. Keep sudo for Docker commands.

## 4. Download the application

```bash
mkdir -p ~/Desktop/labs
cd ~/Desktop/labs
git clone https://github.com/lmoroz/bWAPP.git
cd bWAPP
```

On a fresh install, use the commands above. If the bWAPP folder already exists, enter that folder instead of cloning over it. The upstream master revision inspected while preparing these notes was d34520de7dfad526913706e9772aae6e9aa34916; the user's exact checkout revision was not recorded. Record your own revision with git rev-parse HEAD.

## 5. Create the local Compose configuration

Run this inside the upstream bWAPP folder:

```bash
cat > compose.local.yml <<'EOF'
services:
  web:
    build: .
    ports:
      - "127.0.0.1:8080:80"
    depends_on:
      - db

  db:
    image: mysql:5.7
    environment:
      MYSQL_ALLOW_EMPTY_PASSWORD: "yes"
    volumes:
      - db_data:/var/lib/mysql

volumes:
  db_data:
EOF
```

The web container reaches MySQL through Docker's private Compose network. The application is deliberately vulnerable, so the guide uses a local browser and a loopback port binding for training.

## 6. Failure observed and diagnosis

The MySQL image downloaded successfully. The web build stopped at Dockerfile line 2:

```dockerfile
RUN apt-get update && apt-get install -y iputils-ping dnsutils
```

The log contained 404 Not Found for Bullseye security versions of libcap2, libcap2-bin, bind9-libs, bind9-host, bind9-dnsutils, dnsutils, and libpam-cap. The build finished with exit code 100. Importantly, apt-get update had completed; the failure was during package download.

This matches Debian's documented Bullseye repository transition: Debian 11 LTS ended on 31 August 2026, and Debian bug 1147093 records missing security package downloads and confirmation that bullseye-security became available on archive.debian.org on 4 October 2026. The failed downloads do not indicate an Apache port conflict or a Kali host APT failure.

## 7. Apply the working archive fix

The successful fix changed the container's security repository from http://deb.debian.org/debian-security to https://archive.debian.org/debian-security, removed its old package lists, and added Acquire::Check-Valid-Until=false to apt-get update. Signature verification remains enabled. The validity-date exception supports archived metadata; it does not restore ongoing security updates.

For the next installation, the following repeat-safe Python block applies the same changes. It saves Dockerfile.before-fix once, leaves an already patched Dockerfile unchanged, and stops if the upstream install line differs.

```bash
python3 - <<'PY'
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
PY
```

This changes the Dockerfile in your lab checkout. It does not edit Kali's /etc/apt/sources.list. Keep the PHP 7.4 runtime for this recorded setup; a change to PHP 8 requires separate compatibility checks.

## 8. Build, start, and initialise

```bash
sudo docker compose -f compose.local.yml build --no-cache web
sudo docker compose -f compose.local.yml up -d
sudo docker compose -f compose.local.yml ps
```

Only continue to up -d after the build finishes successfully. The first build can take several minutes. The ps command should show both web and db running; database readiness can take longer than container startup.

In Firefox inside Kali:

1. Open http://127.0.0.1:8080/bWAPP/install.php.
2. Click the “here” link to create and populate the database.
3. If the database is not ready yet, wait about 30 seconds and refresh.
4. Open http://127.0.0.1:8080/bWAPP/login.php.
5. Log in with username bee and password bug.

Do not rerun install.php just to restart an existing working lab. The database volume preserves the initialisation.

## 9. Next-session commands

Start after shutdown:

```bash
cd ~/Desktop/labs/bWAPP
sudo systemctl start docker
sudo docker compose -f compose.local.yml up -d
```

Stop at the end of a session:

```bash
sudo docker compose -f compose.local.yml stop
```

Show status and recent logs:

```bash
sudo docker compose -f compose.local.yml ps
sudo docker compose -f compose.local.yml logs --tail=60
```

Stop and remove the containers while keeping the named database volume:

```bash
sudo docker compose -f compose.local.yml down
```

Avoid down -v when keeping your lab data: it removes the named database volume. Enable Docker automatically at boot only if desired: sudo systemctl enable docker. Starting Docker does not automatically start this Compose stack.

## 10. Troubleshooting

| Symptom | Check / action |
|---|---|
| Another Bullseye security 404 | Check that the Dockerfile contains the archive URL; rebuild web with --no-cache |
| A later 404 from the main Bullseye repository | Inspect the exact URL and current Debian archive status; this fix only covers the recorded security source |
| Cannot connect to Docker daemon | sudo systemctl start docker; sudo systemctl status docker --no-pager |
| Permission denied on Docker socket | Run the Docker command with sudo |
| compose.local.yml not found | cd ~/Desktop/labs/bWAPP; ls compose.local.yml |
| Port 8080 already allocated | sudo ss -ltnp 'sport = :8080'; change the host side of the mapping to 127.0.0.1:8081:80 and run up -d |
| Database connection refused | Check db status and logs; wait for MySQL startup, then refresh install.php |
| Browser connection refused | Check web logs; use Firefox inside Kali and verify the port mapping |
| Docker downloads time out | Check Kali network access and registry connectivity; repository edits cannot fix a network outage |

If the port changes to 8081, use 8081 in all browser URLs. Inspect the service occupying a port before stopping it.

## 11. Verification record

| Check | Evidence / result |
|---|---|
| Upstream dependencies and login instructions | Read from the linked repository files |
| Initial failure | Supplied Docker build output: Debian security package 404s, exit 100 |
| Repair and application operation | User confirmed the installation worked after the fix |
| Reusable patch helper | Transformation and repeat-run checks performed during document preparation |
| Fresh container build by the document author | Not performed; the runtime outcome is the user's reported result |

The archived runtime supports reproducing this training setup. It is not a current production deployment baseline. The provided patch helper is intended for this upstream Dockerfile; review it if the upstream base or package sources change.

## 12. References

- [Upstream repository and setup](https://github.com/lmoroz/bWAPP/tree/master)
- [Upstream Dockerfile](https://github.com/lmoroz/bWAPP/blob/master/Dockerfile)
- [Upstream installation / credentials](https://github.com/lmoroz/bWAPP/blob/master/INSTALL.txt)
- [Installing Docker on Kali](https://www.kali.org/docs/containers/installing-docker-on-kali/)
- [Debian Bullseye LTS end of life](https://www.debian.org/News/2026/20260831)
- [Debian archive transition, bug 1147093](https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1147093)
- [Docker build best practices](https://docs.docker.com/build/building/best-practices/)
