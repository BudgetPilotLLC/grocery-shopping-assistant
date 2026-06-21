# Server Docker Deployment

This app can run as a small Docker service on the Jellyfin/server machine.

## Local Build Test

```powershell
docker compose up --build
```

Open:

```text
http://127.0.0.1:8787
```

## Server Shape

On the server:

```bash
git clone <repo-or-copy-folder> grocery-assistant
cd grocery-assistant
cp .env.example .env
nano .env
docker compose up -d --build
```

Then use:

```text
http://SERVER_IP:8787
```

The `data` folder is mounted as a volume, so your catalog CSV and grocery list file survive container rebuilds.

If you want OneDrive as the list source on the server, sync or mount a OneDrive folder into the `data` volume and set `GROCERY_LIST_PATH` to that mounted file. See [onedrive.md](onedrive.md).

For Amazon, put only official API/provider credentials in `.env`. Do not put your Amazon shopping account username/password in the Docker environment. See [amazon.md](amazon.md).

## Reverse Proxy Optional

For home-only use, a direct LAN port is enough. If this gets exposed through a reverse proxy later, keep a token on `/api/apple-note` and put it behind HTTPS.
