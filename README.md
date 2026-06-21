# Grocery Shopping Assistant

A local grocery price board that reads a grocery list, compares matching products by store, and shows the cheapest option plus price per serving.

The current app works with a OneDrive-friendly grocery list file at `data/grocery-list.txt` and a local catalog file at `data/catalog.csv`. It is built so live providers can be added later, with Instacart as the cleanest route for many local grocery retailers.

## Run It

```powershell
python -m app.server
```

Then open:

```text
http://127.0.0.1:8787
```

To accept Apple Shortcuts posts from an iPhone on the same Wi-Fi, run it on your LAN interface:

```powershell
$env:GROCERY_ASSISTANT_TOKEN="choose-a-long-token"
python -m app.server --host 0.0.0.0 --port 8787
```

The app prints the local URL and the Apple Note webhook URL when it starts.

## Docker

```powershell
Copy-Item .env.example .env
# edit .env
$env:GROCERY_ASSISTANT_TOKEN="choose-a-long-token"
docker compose up --build
```

For the Jellyfin/server deployment notes, see [docs/server-docker.md](docs/server-docker.md).

## Public GitHub Pages Site

The Amazon Associates-facing public site lives in `docs/` and is designed to be served by GitHub Pages:

```text
https://budgetpilotllc.github.io/grocery-shopping-assistant/
```

Setup steps are in [docs/github-pages.md](docs/github-pages.md).

The site includes a starter recommendations page at `/recommendations.html`. Its Amazon links currently use the Associate tag `budgetpilotllc-20`; update that tag if Amazon assigned a different Store ID.

## How It Works

- Paste a grocery list into the app, or POST note text to `/api/apple-note`.
- The parser understands list lines such as `2 lb chicken breast`, `milk x2`, `12 eggs`, and `rice (servings 10)`.
- The matcher compares each item against `data/catalog.csv`.
- The result shows:
  - cheapest split-store basket
  - cheapest single-store basket
  - price per serving
  - missing items
  - store-by-store totals

## OneDrive List

Since this project is already inside OneDrive, the simplest phone workflow is to edit:

```text
data/grocery-list.txt
```

The assistant reads that synced file whenever it loads or refreshes. To point it at a different OneDrive file:

```powershell
$env:GROCERY_LIST_PATH="$env:USERPROFILE\OneDrive\Grocery List.txt"
python -m app.server
```

See [docs/onedrive.md](docs/onedrive.md).

## Apple Notes

Apple does not provide a general Apple Notes API. Apple Developer Technical Support answered that there is no CRUD API for Apple Notes, and AppleScript access is macOS-only. Because this project is running on Windows, the practical bridge is Apple Shortcuts: have a Shortcut read the shared note and POST the note body to this app. OneDrive is cleaner if you are happy editing a synced grocery list file.

See [docs/apple-shortcuts.md](docs/apple-shortcuts.md).

Source: [Apple Developer Forums: Apple Notes API](https://origin-devforums.apple.com/forums/thread/813810?answerId=873771022)

## Live Prices

For live prices around your ZIP code, the most realistic first provider is Instacart Developer Platform because its current docs describe nearby retailers, shopping list matching, and real-time pricing/inventory. Amazon requires the affiliate/product API path. Publix and Aldi do not appear to offer broad public price APIs, so they usually need Instacart, a partner feed, a manual catalog import, or a paid data provider.

See [docs/live-pricing.md](docs/live-pricing.md).

Amazon and Amazon Fresh are separate stores in the catalog and UI. See [docs/amazon.md](docs/amazon.md) for the live-price options and limitations.

Sources:

- [Instacart Developer Platform](https://docs.instacart.com/developer_platform_api)
- [Amazon Product Advertising API 5.0](https://webservices.amazon.com/paapi5/documentation/)
- [Amazon PA-API buying price notice](https://webservices.amazon.com/paapi5/documentation/use-cases/buying-price.html)
- [Sam's Advertising Partners Catalog Item Search](https://developer.samsclub.com/API/catalog-item-search/)

## Catalog Format

Edit `data/catalog.csv` with your own prices. The sample rows are demonstrative placeholders, not a live price feed.

Required columns:

```csv
store,product,category,aliases,size_qty,size_unit,package_desc,price,servings,url,last_updated,zip,notes
```

Useful notes:

- `aliases` is a semicolon-separated list used for matching.
- `size_qty` and `size_unit` are used to decide how many packages are needed.
- `servings` drives price-per-serving.
- `zip` lets you keep location-specific prices.

## Tests

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```
