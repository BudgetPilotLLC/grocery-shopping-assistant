# PantryCents Mac Codex Handoff

This file is for starting a fresh Codex session on a Mac with enough context to continue building PantryCents without needing the original conversation.

## Project Snapshot

- App name: `PantryCents`
- GitHub account: `BudgetPilotLLC`
- Main repo: `https://github.com/BudgetPilotLLC/grocery-shopping-assistant`
- Public project site: `https://budgetpilotllc.github.io/grocery-shopping-assistant/`
- Root GitHub Pages site: `https://budgetpilotllc.github.io/`
- Local Windows source path used by the first Codex instance: `Grocery Shopping Assistant`
- Budgeting app name reserved for the separate product: `FlowMint`

PantryCents is a grocery shopping assistant. It reads a grocery list, matches items to a product catalog, compares store baskets, and shows price-per-serving estimates. It is currently a local prototype with static/sample data and a public affiliate/approval site.

## Current Architecture

```text
app/
  parser.py       Parses grocery list text into structured items.
  pricing.py      Matches grocery items to catalog offers and computes basket totals.
  server.py       Python stdlib HTTP server and JSON API.
web/
  index.html      Local app UI.
  app.js          Browser logic for loading list data and displaying comparisons.
  styles.css      Local app styling.
data/
  grocery-list.txt Sample grocery list.
  catalog.csv      Sample/manual catalog, not live pricing.
docs/
  index.html      GitHub Pages marketing/affiliate approval page.
  recommendations.html Starter affiliate recommendation page.
  *.md            Provider, Docker, OneDrive, Apple Shortcuts notes.
tests/
  test_parser.py
  test_pricing.py
```

The project intentionally has no Python package dependencies right now. It uses only the Python standard library.

## Setup On Mac

```bash
git clone https://github.com/BudgetPilotLLC/grocery-shopping-assistant.git PantryCents
cd PantryCents
python3 -m unittest discover -s tests -p "test_*.py" -v
python3 -m app.server
```

Open:

```text
http://127.0.0.1:8787
```

For LAN/iPhone testing:

```bash
export GROCERY_ASSISTANT_TOKEN="choose-a-long-random-token"
python3 -m app.server --host 0.0.0.0 --port 8787
```

Then use the printed `/api/apple-note` URL from the server output.

## OneDrive On Mac

The default list file is:

```text
data/grocery-list.txt
```

If using OneDrive on macOS, set `GROCERY_LIST_PATH` to the actual synced file path. Common OneDrive locations vary by install, for example:

```bash
export GROCERY_LIST_PATH="$HOME/Library/CloudStorage/OneDrive-Personal/Grocery List.txt"
python3 -m app.server
```

Do not hard-code personal local paths into committed docs or source files.

## Environment Variables

Create a private `.env` from `.env.example` when running with Docker or future provider integrations:

```bash
cp .env.example .env
```

Do not commit `.env`.

Current placeholders:

- `GROCERY_ASSISTANT_TOKEN`
- `GROCERY_LIST_PATH`
- `AMAZON_PROVIDER`
- `AMAZON_MARKETPLACE`
- `AMAZON_ASSOCIATE_TAG`
- `AMAZON_ACCESS_KEY_ID`
- `AMAZON_SECRET_ACCESS_KEY`
- `AMAZON_CREATORS_API_TOKEN`
- `AMAZON_FRESH_PROVIDER`
- `AMAZON_FRESH_ZIP`

Future affiliate/provider IDs should be added to `.env.example` as placeholders first, then read from private `.env` values.

## Affiliate And Provider Status

The user has signed up for multiple affiliate programs and is close to Amazon API access. At last handoff, Amazon had 7 out of 10 recommended/sold products toward access eligibility.

Important distinction:

- Affiliate links are for monetization and tracking.
- Price APIs/data feeds are for actual grocery comparison.

Do not scrape logged-in Amazon, Walmart, Sam's, Publix, Aldi, or Instacart account pages. Prefer official APIs, affiliate feeds, developer platforms, manual catalog import, or user-approved assisted export workflows.

Current likely providers/routes:

- Amazon / Amazon Fresh: Amazon Associates and Product Advertising API once eligible. Fresh is location-sensitive.
- Instacart: best candidate for local grocery availability/pricing and stores like Publix/Aldi when supported.
- Walmart: affiliate links available; live price data may need API/feed/provider route.
- Sam's Club: affiliate/creator routes exist; live catalog search may be possible through approved developer/API access.
- Publix/Aldi: likely via Instacart, manual catalog, affiliate/creator program, or approved partner feed.

## Immediate Next Build Step

Recommended next coding task:

1. Add an affiliate link generation module, probably `app/affiliate_links.py`.
2. Add safe placeholder env vars for affiliate IDs in `.env.example`.
3. Add tests for link generation.
4. Extend `data/catalog.csv` with optional columns only if needed, such as `affiliate_url`, `store_product_id`, or `provider`.
5. Update the UI so product rows can show a store link when available.
6. Keep price calculation independent from affiliate tracking.

Suggested env placeholders:

```text
AMAZON_ASSOCIATE_TAG=
WALMART_AFFILIATE_ID=
SAMS_AFFILIATE_ID=
INSTACART_AFFILIATE_ID=
ALDI_AFFILIATE_ID=
IMPACT_ACCOUNT_ID=
RAKUTEN_SITE_ID=
```

## Public Site Notes

The GitHub Pages site in `docs/` is part marketing page, part affiliate approval page. It includes:

- PantryCents explanation.
- Amazon Associate disclosure.
- Starter recommendations page.
- Impact/Instacart verification tag and content segment.

At handoff, both of these live URLs included the Impact verification token:

```text
https://budgetpilotllc.github.io/
https://budgetpilotllc.github.io/grocery-shopping-assistant/
```

Current token used:

```text
Impact-Site-Verification: 79274455-e686-468c-b9ef-aafa080c1880
```

The root site lives in a separate repo:

```text
https://github.com/BudgetPilotLLC/BudgetPilotLLC.github.io
```

Only edit that repo if working on account-level GitHub Pages or affiliate verification.

## Verification Commands

Run these before pushing:

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
git status -sb
```

Check for accidental local machine/network info before publishing:

```bash
git grep -n -I -E "C:\\\\Users\\\\|192\\.168\\.|10\\.[0-9]+\\.|172\\.(1[6-9]|2[0-9]|3[0-1])\\." -- . ':!docs/assets/app-preview.png'
```

Expected result: no output.

Check for accidental secret-looking content:

```bash
git grep -n -I -E "password|secret|token|api[_-]?key|access[_-]?key|client[_-]?secret|refresh[_-]?token" -- .
```

Placeholders and source variable names are okay. Real credentials are not.

## Suggested First Prompt For Mac Codex

```text
Read MAC_CODEX_HANDOFF.md and the project README. Then inspect app/parser.py, app/pricing.py, app/server.py, web/app.js, and data/catalog.csv. After that, implement the next affiliate-link layer safely: env placeholders, a tested link-generation module, and UI links where catalog rows have enough data. Keep price calculations separate from affiliate tracking and do not add real credentials to the repo.
```
