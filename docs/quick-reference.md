# bWAPP Kali: Next-Session Quick Reference

**Folder:** ~/Desktop/labs/bWAPP  
**Browser:** Firefox inside Kali  
**Login URL:** http://127.0.0.1:8080/bWAPP/login.php  
**Account:** bee / bug

## Start

```bash
cd ~/Desktop/labs/bWAPP
sudo systemctl start docker
sudo docker compose -f compose.local.yml up -d
```

## Stop

```bash
sudo docker compose -f compose.local.yml stop
```

## Status and logs

```bash
sudo docker compose -f compose.local.yml ps
sudo docker compose -f compose.local.yml logs --tail=60
```

## Rebuild only when needed

```bash
sudo docker compose -f compose.local.yml build --no-cache web
sudo docker compose -f compose.local.yml up -d
```

## First installation only

Open http://127.0.0.1:8080/bWAPP/install.php and click “here”. Do not rerun the installer for a normal restart.

## Remember

- Keep compose.local.yml in the upstream bWAPP folder.
- Use the included archive patch for the recorded Bullseye security 404.
- Keep db_data when retaining the database; down -v removes it.
- Localhost in the Kali VM is different from localhost on the host laptop.
- The complete fresh-install procedure is in the installation report and PDF.
