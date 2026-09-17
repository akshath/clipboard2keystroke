# Clipboard2Keystroke

A lightweight Python utility that types your clipboard contents as simulated keystrokes. Useful for applications or remote desktops or websites that block paste (`Ctrl+V`) but still accept keyboard input.

## How It Works

1. The script registers a global hotkey and runs in the background.
2. When you press the hotkey, it reads the current clipboard contents and types them out character by character as if you were typing on the keyboard.

## Install

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

## Prerequisites

- Python >= 3.10 (installed automatically by `uv`)
- **Linux**: requires root privileges (the `keyboard` library needs access to `/dev/input`)
- **macOS**: requires accessibility permissions for the terminal/app running the script

## Running from a clone

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

Once running, press **Ctrl+Alt+K** (Windows/Linux) or **Ctrl+Option+K** (macOS) to type out whatever is currently on your clipboard.

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

## Testing

Run the unit tests with:

```bash
uv run --with pytest --with keyboard --with pyperclip --with pynput pytest test_clipboard2keystroke.py -v
```

## Dependencies

| Package | Purpose |
|---|---|
| [pyperclip](https://github.com/asweigart/pyperclip) | Cross-platform clipboard access |
| [keyboard](https://github.com/boppreh/keyboard) | Global hotkey and keystroke simulation on Windows/Linux |
| [pynput](https://github.com/moses-palmer/pynput) | Global hotkey and keystroke simulation on macOS |

## License

[MIT](LICENSE)
