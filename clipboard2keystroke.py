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

import platform
import pyperclip
from datetime import datetime

IS_MACOS = platform.system() == 'Darwin'

# macOS uses pynput, which spells hotkeys differently than the keyboard library.
MACOS_HOTKEY = '<ctrl>+<alt>+k'
DEFAULT_HOTKEY = 'ctrl+alt+k'


def type_text(text):
    if IS_MACOS:
        from pynput.keyboard import Controller as KbController
        KbController().type(text)
    else:
        import keyboard
        keyboard.write(text)


def send_clipboard():
    print('sending clipboard key', datetime.now())
    try:
        type_text(pyperclip.paste())
    except Exception as exc:
        # Never propagate: on macOS an exception here kills the hotkey listener.
        print(f'failed to send clipboard: {exc}')


def wait_for_hotkey():
    try:
        if IS_MACOS:
            from pynput import keyboard as pynput_keyboard

            print('Waiting for hotkey ctrl+option+k')
            with pynput_keyboard.GlobalHotKeys({MACOS_HOTKEY: send_clipboard}) as h:
                h.join()
        else:
            import keyboard

            print(f'Waiting for hotkey {DEFAULT_HOTKEY}')
            keyboard.add_hotkey(DEFAULT_HOTKEY, send_clipboard)
            keyboard.wait()
    except KeyboardInterrupt:
        print('\nstopped')


if __name__ == '__main__':
    wait_for_hotkey()
