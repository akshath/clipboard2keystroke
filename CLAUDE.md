# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A single-script Python utility that listens for a global hotkey and types the current clipboard contents as simulated keystrokes. Useful when paste is blocked but keyboard input is accepted.

## Running

Uses `uv` as the script runner (inline dependency metadata via PEP 723):

```
uv run clipboard2keystroke.py
```

Platform-specific wrappers: `run.bat` (Windows), `run.sh` (Unix).

There is a legacy `Pipfile` for pipenv, but `uv run` is the current approach.

## Dependencies

Declared inline at the top of `clipboard2keystroke.py`:
- `keyboard` - global hotkey registration and keystroke simulation
- `pyperclip` - cross-platform clipboard access

Requires Python >= 3.10. The `keyboard` library requires root/admin on Linux.

## Architecture

Single file (`clipboard2keystroke.py`): registers `ctrl+option+k` as a global hotkey via `keyboard.add_hotkey`, and on trigger calls `send_clipboard()` which reads the clipboard with `pyperclip.paste()` and types it via `keyboard.write()`. The main thread blocks on `keyboard.wait()`.

Note: the hotkey is currently set to `ctrl+option+k` (macOS-style). The commented-out line shows the Windows/Linux variant `ctrl+alt+k`.
