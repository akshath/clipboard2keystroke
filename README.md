# Clipboard2Keystroke

A lightweight Python utility that types your clipboard contents as simulated keystrokes. Useful for applications or remote desktops that block paste (`Ctrl+V`) but still accept keyboard input.

## How It Works

1. The script registers a global hotkey and runs in the background.
2. When you press the hotkey, it reads the current clipboard contents and types them out character by character as if you were typing on the keyboard.

## Prerequisites

- Python >= 3.10
- [uv](https://github.com/astral-sh/uv) (recommended) or [pipenv](https://pipenv.pypa.io/)
- **Linux**: requires root privileges (the `keyboard` library needs access to `/dev/input`)
- **macOS**: requires accessibility permissions for the terminal/app running the script

## Usage

### With uv (recommended)

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

### With pipenv

```bash
pipenv install
pipenv run python clipboard2keystroke.py
```

### Hotkey

Once running, press **Ctrl+Alt+K** (Windows/Linux) or **Ctrl+Option+K** (macOS) to type out whatever is currently on your clipboard.

Press **Ctrl+C** in the terminal to stop the script.

## Dependencies

| Package | Purpose |
|---|---|
| [keyboard](https://github.com/boppreh/keyboard) | Global hotkey registration and keystroke simulation |
| [pyperclip](https://github.com/asweigart/pyperclip) | Cross-platform clipboard access |
