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

import keyboard
import pyperclip
from datetime import datetime

def check_if_keyPressed():

    #while True:
    #    if keyboard.is_pressed("q"):
    #        print("You pressed q")
    #        break
            
   #keyboard.add_hotkey('ctrl+alt+k', send_clipboard)
   keyboard.add_hotkey('ctrl+option+k', send_clipboard)

def send_clipboard():
    print('sending clipboard key',datetime.now())
    keyboard.write(pyperclip.paste())


if __name__ == '__main__':
    check_if_keyPressed()
    print('Waiting for hotkey Ctrl+Alt+K')
    

    # Block forever, like `while True`.
    keyboard.wait()