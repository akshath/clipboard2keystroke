# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "keyboard",
#   "pyperclip",
# ]
# ///

# -------------------------------
# send clipboard to keystroke
# shortcut ctrl+alt+k
# -------------------------------

import platform
import keyboard
import pyperclip
from datetime import datetime

HOTKEY = 'ctrl+option+k' if platform.system() == 'Darwin' else 'ctrl+alt+k'

def check_if_keyPressed():
   keyboard.add_hotkey(HOTKEY, send_clipboard)

def send_clipboard():
    print('sending clipboard key',datetime.now())
    keyboard.write(pyperclip.paste())


if __name__ == '__main__':
    check_if_keyPressed()
    print(f'Waiting for hotkey {HOTKEY}')

    # Block forever, like `while True`.
    keyboard.wait()