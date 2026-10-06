# Installing bWAPP on Kali Linux with Docker—and Fixing the Debian 404 Error

**Subtitle:** A practical walkthrough from a failed PHP container build to a working local web security lab.

**Author:** Rajsegar Alagarathnam  
**Draft date:** 6 October 2026  
**Suggested tags:** Kali Linux, Docker, Cybersecurity, Linux, Web Security

I wanted to set up bWAPP on Kali Linux so I could practise web security in a local lab. I used the lmoroz/bWAPP repository because it includes a Docker setup for PHP and MySQL.

The installation initially failed. Docker downloaded the database image, but the web container stopped while installing Debian packages. Several downloads returned 404 Not Found.

After correcting the Debian security repository inside the container build and rebuilding the image, bWAPP worked. These are the steps I followed, with a repeat-safe version of the fix for the next installation.

## What runs inside the lab

bWAPP is a deliberately vulnerable PHP web application for security training. In this setup, a web container runs Apache and PHP 7.4, and a database container runs MySQL 5.7. Kali runs Docker and the browser.

I used the address http://127.0.0.1:8080/bWAPP/. Port 8080 belongs to Kali, while port 80 belongs to Apache inside the container. MySQL stays on the private Compose network and is not published on the host.

This is a legacy training environment. The archive fix makes the old packages available again; it does not turn the runtime into a supported production platform.

## Step 1: Install the tools

In Kali's terminal:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose git python3
sudo systemctl start docker
sudo docker compose version
```

Kali's container engine package is docker.io. I used sudo for Docker commands, so I did not need to change Docker group membership.

## Step 2: Clone bWAPP

```bash
mkdir -p ~/Desktop/labs
cd ~/Desktop/labs
git clone https://github.com/lmoroz/bWAPP.git
cd bWAPP
```

I kept the lab in ~/Desktop/labs/bWAPP. If you already have that checkout, enter it instead of running git clone again.

## Step 3: Add a local Compose file

Inside the bWAPP folder, I created compose.local.yml:

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

The loopback binding keeps the web application accessible through the local Kali browser. The database service name is db, which matches the application's existing connection settings. The db_data volume retains the database when containers are stopped and recreated.

## The problem: package lists existed, but downloads failed

My first build used:

```bash
sudo docker compose -f compose.local.yml up -d --build
```

The build stopped at:

```dockerfile
RUN apt-get update && apt-get install -y iputils-ping dnsutils
```

The terminal showed 404 errors for packages including libcap2, bind9-libs, and dnsutils. The final message reported exit code 100.

One detail helped explain the issue: apt-get update had succeeded. The failure came when APT tried to download package versions from the Bullseye security repository.

Debian 11 Bullseye reached the end of its LTS period on 31 August 2026. Debian's bug report 1147093 describes the missing security packages and later confirms that bullseye-security became available in the archive on 4 October 2026. That matched the error in my build log.

## Step 4: Fix the security package source

The fix changes the Debian security URL inside the image to archive.debian.org, removes old package lists, and permits archived metadata during apt-get update. It leaves package signature verification enabled.

For a fresh checkout, this Python block applies the same repair and saves a backup. Running it again does not add the patch twice:

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

The change belongs in the lab's Dockerfile. I did not need to replace Kali's own APT repositories. I also kept PHP 7.4 because changing the runtime version would require separate application compatibility checks.

## Step 5: Rebuild and start

```bash
sudo docker compose -f compose.local.yml build --no-cache web
sudo docker compose -f compose.local.yml up -d
sudo docker compose -f compose.local.yml ps
```

The --no-cache option reruns the image build steps. Once the build completes, up -d starts the services in the background. The ps command shows their current state.

## Step 6: Create the database and log in

In Firefox inside Kali, I opened:

http://127.0.0.1:8080/bWAPP/install.php

I clicked the “here” link to create the database, then opened:

http://127.0.0.1:8080/bWAPP/login.php

The default application credentials are:

```text
Username: bee
Password: bug
```

If MySQL is still starting, wait briefly and refresh the installer. Container startup and database readiness are separate stages.

## Commands for the next session

After restarting Kali, I can bring the lab back with:

```bash
cd ~/Desktop/labs/bWAPP
sudo systemctl start docker
sudo docker compose -f compose.local.yml up -d
```

When I finish:

```bash
sudo docker compose -f compose.local.yml stop
```

If something is wrong, I check the logs:

```bash
sudo docker compose -f compose.local.yml logs --tail=60
```

I do not need to rebuild the image or rerun install.php for every session. The existing image and database volume remain available. I avoid down -v when I want to retain the database.

## What I learned

The useful clue was where the build failed. Docker image downloads worked, and the package index update worked, but specific Debian security package downloads did not. Reading those stages separately helped identify the repository issue.

I now have a working bWAPP lab and a set of notes I can reuse. Recording the Compose file, the archive repair, and the restart commands makes the next installation easier to follow.

## Sources

- [Upstream repository and setup](https://github.com/lmoroz/bWAPP/tree/master)
- [Upstream Dockerfile](https://github.com/lmoroz/bWAPP/blob/master/Dockerfile)
- [Upstream installation / credentials](https://github.com/lmoroz/bWAPP/blob/master/INSTALL.txt)
- [Installing Docker on Kali](https://www.kali.org/docs/containers/installing-docker-on-kali/)
- [Debian Bullseye LTS end of life](https://www.debian.org/News/2026/20260831)
- [Debian archive transition, bug 1147093](https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1147093)
- [Docker build best practices](https://docs.docker.com/build/building/best-practices/)
