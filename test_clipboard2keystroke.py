from unittest.mock import patch, MagicMock
from clipboard2keystroke import send_clipboard, check_if_keyPressed


@patch("clipboard2keystroke.keyboard")
@patch("clipboard2keystroke.pyperclip")
def test_send_clipboard_types_clipboard_contents(mock_pyperclip, mock_keyboard):
    mock_pyperclip.paste.return_value = "hello world"
    send_clipboard()
    mock_keyboard.write.assert_called_once_with("hello world")


@patch("clipboard2keystroke.keyboard")
@patch("clipboard2keystroke.pyperclip")
def test_send_clipboard_handles_empty_clipboard(mock_pyperclip, mock_keyboard):
    mock_pyperclip.paste.return_value = ""
    send_clipboard()
    mock_keyboard.write.assert_called_once_with("")


@patch("clipboard2keystroke.keyboard")
def test_check_if_keyPressed_registers_hotkey(mock_keyboard):
    check_if_keyPressed()
    mock_keyboard.add_hotkey.assert_called_once_with("ctrl+option+k", send_clipboard)
