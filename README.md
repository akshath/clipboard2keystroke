<p align="center">
  <img src="extension/icons/icon128.png" width="96" height="96" alt="Clipboard2Keystroke logo">
</p>

# Clipboard2Keystroke

Types your clipboard contents as simulated keystrokes. Useful for apps, remote desktops and websites that block paste (`Ctrl+V`) but still accept keyboard input.

It comes in two forms:

| | Desktop script | Browser extension |
|---|---|---|
| **Use it for** | Native apps, VMs, remote desktop clients | Web pages, especially login forms |
| **Trigger** | **Ctrl+Shift+K** (on macOS too: Control, not Cmd) | Click the toolbar icon, or **Alt+Shift+K** (macOS: **Option+Shift+K**) |
| **Runs on** | Windows, macOS, Linux (Python via `uv`) | Chrome, Edge, Firefox |
| **Set up** | [Desktop script](#desktop-script) | [Browser extension](#browser-extension-chrome-edge-firefox) |

On macOS, use the extension for password fields. A focused password field turns on Secure Input, which hides your keystrokes from the desktop script (see [Troubleshooting](#troubleshooting)).

## Desktop script

1. The script registers a global hotkey and runs in the background.
2. When you press the hotkey, it reads the current clipboard contents and types them out character by character as if you were typing on the keyboard.

### Install

**macOS / Linux**

```bash
curl -fsSL https://raw.githubusercontent.com/akshath/clipboard2keystroke/main/install.sh | sh
```

**Windows** (PowerShell)

```powershell
irm https://raw.githubusercontent.com/akshath/clipboard2keystroke/main/install.ps1 | iex
```

The installer installs [uv](https://github.com/astral-sh/uv) if it is missing, drops the
script in a data directory, and puts a `clipboard2keystroke` launcher on your PATH. Then:

```bash
clipboard2keystroke     # Linux: sudo clipboard2keystroke
```

<details>
<summary>Options and uninstall</summary>

The shell installer reads `C2K_REF` (git ref, default `main`), `C2K_BIN_DIR`
(default `~/.local/bin`) and `C2K_LIB_DIR` (default
`~/.local/share/clipboard2keystroke`). The PowerShell installer reads `C2K_REF`
and `C2K_DIR` (default `%LOCALAPPDATA%\clipboard2keystroke`).

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/akshath/clipboard2keystroke/main/install.sh | sh -s -- --uninstall
```

```powershell
# Windows
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/akshath/clipboard2keystroke/main/install.ps1))) -Uninstall
```

Neither uninstaller removes `uv`.

</details>

### Prerequisites

- Python >= 3.10 (installed automatically by `uv`)
- **Linux**: requires root privileges (the `keyboard` library needs access to `/dev/input`)
- **macOS**: requires accessibility permissions for the terminal/app running the script

### Running from a clone

Dependencies are declared inline in the script via [PEP 723](https://peps.python.org/pep-0723/), so `uv` handles everything automatically:

```bash
uv run clipboard2keystroke.py
```

Or use the platform wrapper scripts:

```bash
# Windows
run.bat

# macOS / Linux
./run.sh
```

### Hotkey

Once running, press **Ctrl+Shift+K** (on macOS too: Control, not Cmd) to type out whatever is currently on your clipboard.

Press **Ctrl+C** in the terminal to stop the script.

### Typing delay

Characters are typed one at a time with a 100&nbsp;ms pause between them. Adjust the delay (in milliseconds) with `--delay`, or disable it entirely with `--delay 0`:

```bash
clipboard2keystroke --delay 250

./run.sh --delay 0          # running from a clone (same for run.bat)
```

If `--delay` is omitted, the `C2K_DELAY_MS` environment variable is used:

```bash
C2K_DELAY_MS=250 clipboard2keystroke
```

`--delay` always wins over the environment variable, and negative values are treated as `0`.

> **Heads up:** the text goes to whichever window has focus at the moment you press the hotkey, not to the window you copied from. If your clipboard holds a password or other secret, a mistimed hotkey will type it into the wrong place — check what is focused first.

## Browser extension (Chrome, Edge, Firefox)

For web pages, especially login forms, use the browser extension in [`extension/`](extension/).

On macOS, a focused password field (or a browser that leaves it stuck on) turns on **Secure Input**. That hides keystrokes from every other app, so the Python script never sees its hotkey. The extension's shortcut is handled by the browser itself, so it still works.

**Install:**

1. Get the code: `git clone https://github.com/akshath/clipboard2keystroke.git`, or [download the ZIP](https://github.com/akshath/clipboard2keystroke/archive/refs/heads/main.zip) and unzip it.
2. Open `chrome://extensions` (or `edge://extensions`) and turn on **Developer mode**.
3. Click **Load unpacked** and pick the `extension` folder.
4. Optional: pin the icon to the toolbar from the puzzle-piece menu so it's one click away.

To update later, pull or download again, then click the reload icon on the extension's card.

**Install in Firefox** (140 or later): open `about:debugging#/runtime/this-firefox`, click **Load Temporary Add-on** and pick `extension/manifest.json`. Regular Firefox only keeps signed add-ons, so a temporary one is removed when Firefox restarts. For a permanent install, use the version from Firefox Add-ons once it's published.

**Use:** click into a field, then either click the extension's toolbar icon or press **Alt+Shift+K** (on macOS **Option+Shift+K**). The extension types the clipboard into that field one character at a time. It uses a different shortcut from the Python script so that running both never types twice.

- Newlines are skipped in single-line fields, so a password copied with a trailing newline never submits the form.
- Typing stops if focus leaves the field.
- The toolbar icon shows the result briefly: **OK**, **?** (no text field focused), **STOP** (focus moved), **ERR** (the page can't be scripted, such as `chrome://` pages or the web store). Hover the icon for details.
- Right-click the toolbar icon and choose **Options** for the settings page: typing speed (default 100 ms per character), the current shortcut, a test field to try the speed, and what each badge means. The **Change shortcut** button opens the browser's shortcut settings (`chrome://extensions/shortcuts`, or in Firefox **about:addons** › gear menu › **Manage Extension Shortcuts**).

It works only inside browser tabs. For native apps, VMs and remote desktop clients, use the Python script.

### Publishing

`./package.sh` builds `dist/clipboard2keystroke-<version>.zip` for the Chrome Web Store, Edge Add-ons and Firefox Add-ons (one zip works for all three). [`store/HOW_TO_PUBLISH.md`](store/HOW_TO_PUBLISH.md) walks through publishing and releasing updates; [`store/STORE_LISTING.md`](store/STORE_LISTING.md) has the listing text, permission justifications and images to upload. `store/render.sh` regenerates the images. The privacy policy is [`PRIVACY.md`](PRIVACY.md).

## Troubleshooting

**macOS: the desktop script is running but the hotkey does nothing.** Another app has turned on Secure Input, usually a browser with a password field focused (Chromium browsers sometimes leave it stuck on). While it is on, macOS hides keystrokes from every other app. Find out which app:

```bash
ioreg -l -w 0 | grep -o '"kCGSSessionSecureInputPID"=[0-9]*'
ps -p <that PID>
```

Click out of the password field or quit that app. For web pages, use the browser extension instead: it is not affected.

## Testing

Desktop script unit tests:

```bash
uv run --with pytest --with keyboard --with pyperclip --with pynput pytest test_clipboard2keystroke.py -v
```

Extension typing tests, in headless Chrome:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless \
  --virtual-time-budget=10000 --dump-dom "file://$PWD/extension/test/typer-test.html" \
  | grep -E '^(PASS|FAIL|ALL)'
```

## Dependencies

| Package | Purpose |
|---|---|
| [pyperclip](https://github.com/asweigart/pyperclip) | Cross-platform clipboard access |
| [keyboard](https://github.com/boppreh/keyboard) | Global hotkey and keystroke simulation on Windows/Linux |
| [pynput](https://github.com/moses-palmer/pynput) | Global hotkey and keystroke simulation on macOS |

## License

[MIT](LICENSE)
