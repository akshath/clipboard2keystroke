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


if __name__ == '__main__':
    wait_for_hotkey()
