# Pulse

Shows what you're listening to or watching on **YouTube Music** and **YouTube** in your Discord profile — or any custom status you set yourself.

- Auto status from YouTube Music ("Listening to") and YouTube ("Watching"), with cover, progress bar and a button
- Custom status: type, title, description, image, button and timer
- Tray icon, autostart with Windows, minimal dark UI
- No Discord token or account access — only the official Rich Presence API

## How it works

```
Browser tab ──► extension ──► Pulse (127.0.0.1:48200) ──► Discord Rich Presence
```

The extension reads the current media session from the page and posts it to the local app, which talks to the Discord desktop client.

## Setup

1. Create an application at <https://discord.com/developers/applications>. Its name is what appears in your status ("Listening to **name**"). Copy the **Application ID**.
2. Install dependencies and run:

   ```bash
   pip install -r requirements.txt
   python main.py
   ```

3. Open **Settings** in the app and paste the Application ID.
4. Install the browser extension: open `chrome://extensions`, enable *Developer mode*, click *Load unpacked* and pick the `extension` folder. Reload any open YouTube tabs.

The Discord desktop client must be running on the same machine, and *Settings → Activity Privacy → Share your detected activity* must be enabled.

> If you publish your own build, set `APP_ID` in `pulse/constants.py` so users don't have to create an application themselves.

## Build an .exe

```bat
build.bat
```

The result is in `dist/`: `Pulse.exe` plus the `extension` folder. Keep them side by side.

## Configuration

Settings are stored in `%APPDATA%\Pulse\config.json`. The local port is defined in `pulse/constants.py` and `extension/background.js` — change both if you need another one.

## Project layout

```
main.py              entry point
pulse/
  presence.py        Discord connection and activity logic
  server.py          local receiver for the extension
  ui.py              interface
  tray.py            tray icon
  config.py          settings storage
  autostart.py       Windows autostart
extension/           browser extension (Manifest V3)
```

## License

MIT
