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
import time
from datetime import datetime

IS_MACOS = platform.system() == 'Darwin'

# macOS uses pynput, which spells hotkeys differently than the keyboard library.
MACOS_HOTKEY = '<ctrl>+<alt>+k'
DEFAULT_HOTKEY = 'ctrl+alt+k'

# Default per-character delay in milliseconds (0 disables the delay).
DELAY_MS = 100.0


def type_text(text, delay_ms=0.0):
    delay = delay_ms / 1000.0
    if IS_MACOS:
        from pynput.keyboard import Controller as KbController
        kb = KbController()
        if delay:
            for ch in text:
                kb.type(ch)
                time.sleep(delay)
        else:
            kb.type(text)
    else:
        import keyboard
        if delay:
            for ch in text:
                keyboard.write(ch)
                time.sleep(delay)
        else:
            keyboard.write(text)


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
        type_text(pyperclip.paste(), DELAY_MS)
    except Exception as exc:
        # Never propagate: on macOS an exception here kills the hotkey listener.
        print(f'failed to send clipboard: {exc}')


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
                                       send_clipboard) as listener:
                listener.join()
        else:
            import keyboard

            print(f'Waiting for hotkey {DEFAULT_HOTKEY}')
            keyboard.add_hotkey(DEFAULT_HOTKEY, send_clipboard)
            keyboard.wait()
    except KeyboardInterrupt:
        print('\nstopped')


def main(argv=None):
    global DELAY_MS
    DELAY_MS = resolve_delay(argv)
    wait_for_hotkey()


if __name__ == '__main__':
    main()
