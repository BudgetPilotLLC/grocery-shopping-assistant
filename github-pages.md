# Apple Notes Bridge

Apple Notes does not expose a general read/write API. This app uses a small webhook so Apple Shortcuts can push note text into the local assistant.

The webhook now writes into the same list file used by the OneDrive flow, usually `data/grocery-list.txt`.

## Start the Assistant on Wi-Fi

```powershell
$env:GROCERY_ASSISTANT_TOKEN="choose-a-long-token"
python -m app.server --host 0.0.0.0 --port 8787
```

Use the printed LAN webhook URL, which will look like:

```text
http://YOUR_PC_LAN_IP:8787/api/apple-note
```

## Shortcut Shape

Create an Apple Shortcut on the iPhone or iPad that owns or can access the shared note:

1. Find the grocery note by name.
2. Get the note body/text.
3. Get Contents of URL.
4. URL: `http://YOUR_PC_LAN_IP:8787/api/apple-note`
5. Method: `POST`
6. Request Body: JSON
7. JSON body:

```json
{
  "text": "Shortcut note text goes here"
}
```

8. Header:

```text
X-Grocery-Token: choose-a-long-token
```

Apple's Shortcuts guide documents using `Get Contents of URL` for API requests:

https://support.apple.com/guide/shortcuts/request-your-first-api-apd58d46713f/ios

## Notes

- Keep the server on your trusted home network.
- Do not expose this app directly to the public internet.
- If Shortcuts cannot read the exact shared note body on your device, the fallback is to copy the note text and paste it into the app.
