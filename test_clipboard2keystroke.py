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
    fake_pynput.HotKey.parse.assert_called_once_with(c2k.MACOS_HOTKEY)
    fake_pynput.HotKey.assert_called_once_with(
        fake_pynput.HotKey.parse.return_value, c2k.send_clipboard)
    fake_pynput.Listener.assert_called_once()
    fake_pynput.Listener.return_value.__enter__.return_value.join \
        .assert_called_once_with()


def _macos_callbacks(fake_pynput):
    """Register the macOS listener and return its (on_press, on_release)."""
    c2k.macos_hotkey_listener(fake_pynput, c2k.MACOS_HOTKEY, c2k.send_clipboard)
    kwargs = fake_pynput.Listener.call_args.kwargs
    return kwargs['on_press'], kwargs['on_release']


def test_macos_callbacks_forward_real_key_events(fake_pynput):
    on_press, on_release = _macos_callbacks(fake_pynput)
    hotkey = fake_pynput.HotKey.return_value
    listener = fake_pynput.Listener.return_value

    on_press('k', False)
    on_release('k', False)

    hotkey.press.assert_called_once_with(listener.canonical.return_value)
    hotkey.release.assert_called_once_with(listener.canonical.return_value)


def test_macos_callbacks_tolerate_missing_injected_argument(fake_pynput):
    # pynput's macOS backend calls on_press/on_release with only the key for
    # media keys (volume, brightness, play/pause); a TypeError here would kill
    # the listener thread.
    on_press, on_release = _macos_callbacks(fake_pynput)

    on_press('<media key>')
    on_release('<media key>')

    fake_pynput.HotKey.return_value.press.assert_called_once()
    fake_pynput.HotKey.return_value.release.assert_called_once()


def test_macos_callbacks_ignore_injected_events(fake_pynput):
    on_press, on_release = _macos_callbacks(fake_pynput)

    on_press('k', True)
    on_release('k', True)

    fake_pynput.HotKey.return_value.press.assert_not_called()
    fake_pynput.HotKey.return_value.release.assert_not_called()


def test_macos_callbacks_swallow_hotkey_errors(fake_pynput):
    on_press, on_release = _macos_callbacks(fake_pynput)
    fake_pynput.HotKey.return_value.press.side_effect = RuntimeError('boom')
    fake_pynput.HotKey.return_value.release.side_effect = RuntimeError('boom')

    on_press('k', False)  # must not raise
    on_release('k', False)  # must not raise


def test_wait_for_hotkey_exits_cleanly_on_ctrl_c(fake_keyboard):
    fake_keyboard.wait.side_effect = KeyboardInterrupt
    with patch.object(c2k, 'IS_MACOS', False):
        c2k.wait_for_hotkey()  # must not raise
