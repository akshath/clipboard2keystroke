# Clipboard2Keystroke

A lightweight Python utility that types your clipboard contents as simulated keystrokes. Useful for applications or remote desktops or websites that block paste (`Ctrl+V`) but still accept keyboard input.

## How It Works

1. The script registers a global hotkey and runs in the background.
2. When you press the hotkey, it reads the current clipboard contents and types them out character by character as if you were typing on the keyboard.

## Prerequisites

- Python >= 3.10
- [uv](https://github.com/astral-sh/uv)
- **Linux**: requires root privileges (the `keyboard` library needs access to `/dev/input`)
- **macOS**: requires accessibility permissions for the terminal/app running the script

## Usage

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
