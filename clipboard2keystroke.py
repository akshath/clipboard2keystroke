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

def send_clipboard():
    print('sending clipboard key', datetime.now())
    if IS_MACOS:
        from pynput.keyboard import Controller as KbController
        kb = KbController()
        kb.type(pyperclip.paste())
    else:
        import keyboard
        keyboard.write(pyperclip.paste())


if __name__ == '__main__':
    if IS_MACOS:
        from pynput import keyboard as pynput_keyboard

        HOTKEY = '<ctrl>+<alt>+k'
        print(f'Waiting for hotkey ctrl+option+k')

        def on_activate():
            send_clipboard()

        with pynput_keyboard.GlobalHotKeys({HOTKEY: on_activate}) as h:
            h.join()
    else:
        import keyboard

        HOTKEY = 'ctrl+alt+k'
        keyboard.add_hotkey(HOTKEY, send_clipboard)
        print(f'Waiting for hotkey {HOTKEY}')
        keyboard.wait()