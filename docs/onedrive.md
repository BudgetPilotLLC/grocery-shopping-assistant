# OneDrive Grocery List

OneDrive is the easiest list source for the current setup because this project already lives under your OneDrive folder on Windows. No cloud API is required if OneDrive is syncing locally.

## Recommended Setup

Use this file as your shared grocery list:

```text
data/grocery-list.txt
```

Because the project is in:

```text
<project-folder>
```

that file should sync through OneDrive. Edit it from your phone, then the assistant reads the synced local copy.

## Custom File Path

If you want the grocery list somewhere else in OneDrive, set `GROCERY_LIST_PATH` before starting the app:

```powershell
$env:GROCERY_LIST_PATH="$env:USERPROFILE\OneDrive\Grocery List.txt"
python -m app.server
```

For Docker:

```yaml
environment:
  GROCERY_LIST_PATH: /app/data/grocery-list.txt
volumes:
  - ./data:/app/data
```

## Phone Editing

The list can stay as plain text:

```text
Groceries:
- 1 gal whole milk
- 12 eggs
- 2 lb chicken breast
- bananas
- rice (servings 10)
```

If editing a `.txt` file from the OneDrive mobile app feels clunky, we can switch the app to read a simple CSV or Excel workbook instead. Excel on iPhone is often nicer for recurring grocery lists.

## Server Options

If the app moves to the Jellyfin/server machine:

- Use `rclone` to sync or mount a OneDrive folder into the Docker container.
- Or add Microsoft Graph OAuth so the app downloads the file directly from OneDrive.

Microsoft Graph represents OneDrive files as `driveItem` resources and supports downloading file content through the driveItem content API:

- https://learn.microsoft.com/en-us/graph/api/resources/driveitem
- https://learn.microsoft.com/en-us/graph/api/driveitem-get-content

Rclone has a OneDrive backend that can mount or sync OneDrive on Linux:

- https://rclone.org/onedrive/

