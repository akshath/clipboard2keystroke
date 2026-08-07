import sys
from unittest.mock import MagicMock, patch

import pytest

import clipboard2keystroke as c2k


@pytest.fixture
def fake_keyboard():
    """Stand in for the `keyboard` module, imported lazily inside the functions."""
    module = MagicMock()
    with patch.dict(sys.modules, {'keyboard': module}):
        yield module


@pytest.fixture
def fake_pynput():
    """Stand in for `pynput` and `pynput.keyboard`."""
    keyboard_module = MagicMock()
    pynput_module = MagicMock(keyboard=keyboard_module)
    with patch.dict(sys.modules, {'pynput': pynput_module,
                                 'pynput.keyboard': keyboard_module}):
        yield keyboard_module


def test_type_text_uses_keyboard_off_macos(fake_keyboard):
    with patch.object(c2k, 'IS_MACOS', False):
        c2k.type_text('hello world')
    fake_keyboard.write.assert_called_once_with('hello world')


def test_type_text_uses_pynput_on_macos(fake_pynput):
    with patch.object(c2k, 'IS_MACOS', True):
        c2k.type_text('hello world')
    fake_pynput.Controller.return_value.type.assert_called_once_with('hello world')


@patch.object(c2k, 'type_text')
@patch.object(c2k, 'pyperclip')
def test_send_clipboard_types_clipboard_contents(mock_pyperclip, mock_type_text):
    mock_pyperclip.paste.return_value = 'hello world'
    c2k.send_clipboard()
    mock_type_text.assert_called_once_with('hello world')


@patch.object(c2k, 'type_text')
@patch.object(c2k, 'pyperclip')
def test_send_clipboard_handles_empty_clipboard(mock_pyperclip, mock_type_text):
    mock_pyperclip.paste.return_value = ''
    c2k.send_clipboard()
    mock_type_text.assert_called_once_with('')


@patch.object(c2k, 'pyperclip')
def test_send_clipboard_swallows_clipboard_errors(mock_pyperclip):
    mock_pyperclip.paste.side_effect = RuntimeError('no clipboard backend')
    c2k.send_clipboard()  # must not raise: it runs inside the hotkey listener


@patch.object(c2k, 'type_text', side_effect=RuntimeError('typing failed'))
@patch.object(c2k, 'pyperclip')
def test_send_clipboard_swallows_typing_errors(mock_pyperclip, _mock_type_text):
    mock_pyperclip.paste.return_value = 'hello world'
    c2k.send_clipboard()  # must not raise


def test_wait_for_hotkey_registers_hotkey_off_macos(fake_keyboard):
    with patch.object(c2k, 'IS_MACOS', False):
        c2k.wait_for_hotkey()
    fake_keyboard.add_hotkey.assert_called_once_with(c2k.DEFAULT_HOTKEY,
                                                     c2k.send_clipboard)
    fake_keyboard.wait.assert_called_once_with()


def test_wait_for_hotkey_registers_hotkey_on_macos(fake_pynput):
    with patch.object(c2k, 'IS_MACOS', True):
        c2k.wait_for_hotkey()
    fake_pynput.GlobalHotKeys.assert_called_once_with(
        {c2k.MACOS_HOTKEY: c2k.send_clipboard})


def test_wait_for_hotkey_exits_cleanly_on_ctrl_c(fake_keyboard):
    fake_keyboard.wait.side_effect = KeyboardInterrupt
    with patch.object(c2k, 'IS_MACOS', False):
        c2k.wait_for_hotkey()  # must not raise
