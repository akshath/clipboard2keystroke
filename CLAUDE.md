# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Workflow

Never commit directly to `main`. Every change goes on a new branch and is raised
as a pull request for review.

## Project Overview

A single-script Python utility that listens for a global hotkey and types the current clipboard contents as simulated keystrokes. Useful when paste is blocked but keyboard input is accepted.

## Running

Uses `uv` as the script runner (inline dependency metadata via PEP 723):

```
uv run clipboard2keystroke.py
```

Platform-specific wrappers: `run.bat` (Windows), `run.sh` (Unix).

## Installers

`install.sh` (POSIX sh, macOS/Linux) and `install.ps1` (Windows) are meant to be
piped from `raw.githubusercontent.com`. Both install `uv` if it is missing,
download `clipboard2keystroke.py` from a git ref (`C2K_REF`, default `main`),
verify the first line is the PEP 723 header, and generate a launcher that
`exec`s `uv run --script` against the installed copy. Both support uninstall
(`--uninstall` / `-Uninstall`) and leave `uv` in place. `install.ps1` must stay
compatible with Windows PowerShell 5.1 — no null-conditional (`?.`) or other
PowerShell 7-only syntax.

Any change to the download URLs must keep them pointing at the raw file path
`clipboard2keystroke.py` at the repo root; the header check will fail otherwise.

## Testing

```
uv run --with pytest --with keyboard --with pyperclip --with pynput pytest test_clipboard2keystroke.py -v
```

The tests never touch the real keyboard: they patch `IS_MACOS` and inject fake
`keyboard` / `pynput` modules into `sys.modules`, so both platform branches are
covered regardless of the host OS.

## Dependencies

Declared inline at the top of `clipboard2keystroke.py`:
- `pyperclip` - cross-platform clipboard access
- `keyboard` - hotkey and keystroke simulation on Windows/Linux
- `pynput` - hotkey and keystroke simulation on macOS

Requires Python >= 3.10. The `keyboard` library requires root on Linux; `pynput`
requires accessibility permissions on macOS.

## Architecture

Single file (`clipboard2keystroke.py`), split by platform because `keyboard` does
not work reliably on macOS:

- `IS_MACOS` selects the backend. The backend modules are imported lazily inside
  the functions so the unused one is never loaded.
- `type_text()` types a string via pynput on macOS, or `keyboard.write`
  elsewhere. On macOS each character goes through `macos_type_char()`, which
  sends the character's real keycode (holding Shift when needed) from
  `build_macos_char_map()`. Don't go back to `Controller.type` for mapped
  characters: pynput's map only covers unshifted characters and sends the rest
  as keycode 0 (the A key) with a unicode override, which remote desktops, VMs
  and browser keydown handlers read as `a`. Control codes and characters with
  no key on the layout still fall back to `Controller.type`.
- `on_hotkey()` is the hotkey callback on both platforms. It runs
  `send_clipboard()` on a worker thread and ignores presses while a paste is
  still typing. Never type inside the listener callback: it blocks the macOS
  event tap for the whole paste, and macOS can disable a stalled tap.
- `send_clipboard()` waits for the hotkey's modifiers to be released
  (`wait_for_modifier_release()`, macOS only, 2 s timeout), reads the clipboard
  and calls `type_text()`. It catches all exceptions on purpose.
- `wait_for_hotkey()` registers the hotkey and blocks. Hotkeys are spelled
  differently per backend: `MACOS_HOTKEY` (`<ctrl>+<shift>+k`) for pynput,
  `DEFAULT_HOTKEY` (`ctrl+shift+k`) for keyboard.
- `macos_hotkey_listener()` builds the pynput listener by hand instead of using
  `pynput.keyboard.GlobalHotKeys`. GlobalHotKeys' callbacks require an
  `injected` argument, but pynput's macOS backend omits it when a media key
  (volume, brightness, play/pause) is pressed, so the resulting `TypeError`
  kills the listener thread. Our callbacks default `injected` to `False` and
  swallow exceptions; keep both properties if this code is touched.
