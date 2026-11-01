# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "keyboard",
#   "pyperclip",
#   "pynput",
# ]
# ///

# -------------------------------
# send clipboard to keystroke
# shortcut ctrl+alt+k (Windows/Linux) / ctrl+option+k (macOS)
# -------------------------------

import argparse
import os
import platform
import pyperclip
import threading
import time
from datetime import datetime

IS_MACOS = platform.system() == 'Darwin'

# macOS uses pynput, which spells hotkeys differently than the keyboard library.
MACOS_HOTKEY = '<ctrl>+<alt>+k'
DEFAULT_HOTKEY = 'ctrl+alt+k'

# Default per-character delay in milliseconds (0 disables the delay).
DELAY_MS = 100.0


# UCKeyTranslate modifier state for Shift ((shiftKey >> 8) & 0xFF).
_UC_SHIFT = 0x02

# Lazily built {char: (keycode, needs_shift)} for the current macOS layout.
_macos_char_map = None


def build_macos_char_map():
    """Map each character the current layout can type to (keycode, shift).

    pynput's own map only covers unshifted characters. Anything else (capitals,
    `!`, `@`, `"` ...) is sent as keycode 0 -- the physical A key -- with a
    unicode override, which apps that read keycodes (remote desktops, VMs,
    browser keydown handlers) see as `a`. Unshifted entries win over shifted.
    """
    from pynput._util.darwin import keycode_context, keycode_to_string

    mapping = {}
    with keycode_context() as context:
        for shift in (False, True):
            for keycode in range(128):
                char = keycode_to_string(context, keycode,
                                         _UC_SHIFT if shift else 0)
                if len(char) == 1 and char.isprintable():
                    mapping.setdefault(char, (keycode, shift))
    return mapping


def macos_type_char(kb, pynput_keyboard, char):
    """Type one character on macOS with its real keycode and Shift state."""
    global _macos_char_map
    if _macos_char_map is None:
        _macos_char_map = build_macos_char_map()
    entry = _macos_char_map.get(char)
    if entry is None:
        # Control codes (newline, tab) and characters with no key on this
        # layout (emoji, accents): fall back to pynput's unicode typing.
        kb.type(char)
        return
    keycode, shift = entry
    key = pynput_keyboard.KeyCode.from_vk(keycode)
    if shift:
        with kb.pressed(pynput_keyboard.Key.shift):
            kb.press(key)
            kb.release(key)
    else:
        kb.press(key)
        kb.release(key)


def type_text(text, delay_ms=0.0):
    delay = delay_ms / 1000.0
    if IS_MACOS:
        from pynput import keyboard as pynput_keyboard
        kb = pynput_keyboard.Controller()
        for ch in text:
            macos_type_char(kb, pynput_keyboard, ch)
            if delay:
                time.sleep(delay)
    else:
        import keyboard
        if delay:
            for ch in text:
                keyboard.write(ch)
                time.sleep(delay)
        else:
            keyboard.write(text)


# How long to wait for the hotkey's modifiers to be released before typing.
MODIFIER_RELEASE_TIMEOUT = 2.0


def macos_modifiers_held():
    """True while Ctrl, Option, Cmd or Shift is physically held."""
    import Quartz
    mask = (Quartz.kCGEventFlagMaskControl | Quartz.kCGEventFlagMaskAlternate
            | Quartz.kCGEventFlagMaskCommand | Quartz.kCGEventFlagMaskShift)
    flags = Quartz.CGEventSourceFlagsState(
        Quartz.kCGEventSourceStateHIDSystemState)
    return bool(flags & mask)


def wait_for_modifier_release(timeout=MODIFIER_RELEASE_TIMEOUT):
    """Block until the hotkey's modifiers are released (macOS only).

    Typing while Ctrl+Option is still held makes some apps read the typed
    characters as shortcuts. Gives up after `timeout` seconds and types anyway.
    """
    if not IS_MACOS:
        return
    deadline = time.monotonic() + timeout
    while macos_modifiers_held() and time.monotonic() < deadline:
        time.sleep(0.01)


def resolve_delay(argv=None):
    """Return the delay in ms: --delay wins, then C2K_DELAY_MS, then 100."""
    parser = argparse.ArgumentParser(
        description='Type clipboard contents as simulated keystrokes on a '
                    'global hotkey.')
    parser.add_argument('--delay', type=float, metavar='MS', default=None,
                        help='delay in milliseconds between each typed '
                             'character (default: 100, 0 disables)')
    args = parser.parse_args(argv)
    delay = args.delay
    if delay is None:
        env = os.environ.get('C2K_DELAY_MS')
        if env is not None:
            delay = float(env)
        else:
            delay = DELAY_MS
    return max(delay, 0.0)


def send_clipboard():
    print('sending clipboard key', datetime.now())
    try:
        wait_for_modifier_release()
        type_text(pyperclip.paste(), DELAY_MS)
    except Exception as exc:
        # Never propagate: this runs on a worker thread with nothing above it.
        print(f'failed to send clipboard: {exc}')


_send_lock = threading.Lock()


def on_hotkey():
    """Hotkey callback: type the clipboard on a worker thread.

    Typing inside the callback would block the listener for the whole paste
    (100 ms per character by default); on macOS a stalled event tap can be
    disabled by the system, killing the hotkey. Presses that arrive while a
    paste is still being typed are ignored instead of queued.
    """
    if not _send_lock.acquire(blocking=False):
        print('still typing previous clipboard, ignoring hotkey')
        return
    try:
        threading.Thread(target=_send_and_release, daemon=True).start()
    except Exception:
        _send_lock.release()
        raise


def _send_and_release():
    try:
        send_clipboard()
    finally:
        _send_lock.release()


def macos_hotkey_listener(pynput_keyboard, hotkey_spec, callback):
    """Build a pynput listener for `hotkey_spec` that survives media keys.

    pynput's GlobalHotKeys cannot be used here: on macOS its press callback is
    invoked without the `injected` argument for media keys (volume, brightness,
    play/pause), which raises a TypeError and kills the listener thread. Driving
    a HotKey from callbacks that tolerate the missing argument avoids that.
    """
    hotkey = pynput_keyboard.HotKey(pynput_keyboard.HotKey.parse(hotkey_spec),
                                    callback)
    listener = None

    def dispatch(handler, key, injected):
        # Skip our own synthetic keystrokes, as GlobalHotKeys does.
        if injected:
            return
        try:
            handler(listener.canonical(key))
        except Exception as exc:
            # Never propagate: an exception here kills the listener thread.
            print(f'failed to handle key {key}: {exc}')

    def on_press(key, injected=False):
        dispatch(hotkey.press, key, injected)

    def on_release(key, injected=False):
        dispatch(hotkey.release, key, injected)

    listener = pynput_keyboard.Listener(on_press=on_press, on_release=on_release)
    return listener


def wait_for_hotkey():
    try:
        if IS_MACOS:
            from pynput import keyboard as pynput_keyboard

            print('Waiting for hotkey ctrl+option+k')
            with macos_hotkey_listener(pynput_keyboard, MACOS_HOTKEY,
                                       on_hotkey) as listener:
                listener.join()
        else:
            import keyboard

            print(f'Waiting for hotkey {DEFAULT_HOTKEY}')
            keyboard.add_hotkey(DEFAULT_HOTKEY, on_hotkey)
            keyboard.wait()
    except KeyboardInterrupt:
        print('\nstopped')


def main(argv=None):
    global DELAY_MS
    DELAY_MS = resolve_delay(argv)
    wait_for_hotkey()


if __name__ == '__main__':
    main()
