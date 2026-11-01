import os
import sys
import threading
from unittest.mock import MagicMock, call, patch

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
    with patch.object(c2k, 'IS_MACOS', True), \
            patch.object(c2k, 'macos_type_char') as mock_type_char:
        c2k.type_text('hi')
    kb = fake_pynput.Controller.return_value
    mock_type_char.assert_has_calls([call(kb, fake_pynput, 'h'),
                                     call(kb, fake_pynput, 'i')])
    assert mock_type_char.call_count == 2


@pytest.fixture(autouse=True)
def no_modifier_wait():
    """Keep send_clipboard from polling real modifier state."""
    with patch.object(c2k, 'wait_for_modifier_release'):
        yield


@patch.object(c2k, 'type_text')
@patch.object(c2k, 'pyperclip')
def test_send_clipboard_types_clipboard_contents(mock_pyperclip, mock_type_text):
    mock_pyperclip.paste.return_value = 'hello world'
    c2k.send_clipboard()
    mock_type_text.assert_called_once_with('hello world', c2k.DELAY_MS)


@patch.object(c2k, 'type_text')
@patch.object(c2k, 'pyperclip')
def test_send_clipboard_handles_empty_clipboard(mock_pyperclip, mock_type_text):
    mock_pyperclip.paste.return_value = ''
    c2k.send_clipboard()
    mock_type_text.assert_called_once_with('', c2k.DELAY_MS)


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
                                                     c2k.on_hotkey)
    fake_keyboard.wait.assert_called_once_with()


def test_wait_for_hotkey_registers_hotkey_on_macos(fake_pynput):
    with patch.object(c2k, 'IS_MACOS', True):
        c2k.wait_for_hotkey()
    fake_pynput.HotKey.parse.assert_called_once_with(c2k.MACOS_HOTKEY)
    fake_pynput.HotKey.assert_called_once_with(
        fake_pynput.HotKey.parse.return_value, c2k.on_hotkey)
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


@patch.object(c2k.time, 'sleep')
def test_type_text_delays_between_chars_off_macos(mock_sleep, fake_keyboard):
    with patch.object(c2k, 'IS_MACOS', False):
        c2k.type_text('ab', delay_ms=50)
    fake_keyboard.write.assert_has_calls([call('a'), call('b')])
    assert fake_keyboard.write.call_count == 2
    mock_sleep.assert_has_calls([call(0.05), call(0.05)])
    assert mock_sleep.call_count == 2


@patch.object(c2k.time, 'sleep')
def test_type_text_delays_between_chars_on_macos(mock_sleep, fake_pynput):
    with patch.object(c2k, 'IS_MACOS', True), \
            patch.object(c2k, 'macos_type_char') as mock_type_char:
        c2k.type_text('ab', delay_ms=50)
    assert mock_type_char.call_count == 2
    mock_sleep.assert_has_calls([call(0.05), call(0.05)])
    assert mock_sleep.call_count == 2


def test_type_text_zero_delay_types_at_once(fake_keyboard):
    with patch.object(c2k, 'IS_MACOS', False):
        c2k.type_text('hello', delay_ms=0)
    fake_keyboard.write.assert_called_once_with('hello')


def test_resolve_delay_defaults_to_module_value(fake_keyboard):
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop('C2K_DELAY_MS', None)
        assert c2k.resolve_delay([]) == c2k.DELAY_MS


def test_resolve_delay_reads_env_var(fake_keyboard):
    with patch.dict(os.environ, {'C2K_DELAY_MS': '250'}):
        assert c2k.resolve_delay([]) == 250.0


def test_resolve_delay_flag_wins_over_env(fake_keyboard):
    with patch.dict(os.environ, {'C2K_DELAY_MS': '250'}):
        assert c2k.resolve_delay(['--delay', '50']) == 50.0


def test_resolve_delay_clamps_negative(fake_keyboard):
    assert c2k.resolve_delay(['--delay', '-10']) == 0.0


@patch.object(c2k, 'wait_for_hotkey')
def test_main_sets_delay_before_waiting(mock_wait):
    c2k.main(['--delay', '250'])
    assert c2k.DELAY_MS == 250.0
    mock_wait.assert_called_once_with()


# --- macOS keycode typing ---------------------------------------------------

CHAR_MAP = {'a': (0, False), 'A': (0, True), '1': (18, False), '!': (18, True)}


@pytest.fixture
def char_map():
    with patch.object(c2k, '_macos_char_map', dict(CHAR_MAP)):
        yield


def test_macos_type_char_unshifted_uses_keycode(fake_pynput, char_map):
    kb = MagicMock()
    c2k.macos_type_char(kb, fake_pynput, 'a')
    fake_pynput.KeyCode.from_vk.assert_called_once_with(0)
    key = fake_pynput.KeyCode.from_vk.return_value
    kb.press.assert_called_once_with(key)
    kb.release.assert_called_once_with(key)
    kb.pressed.assert_not_called()
    kb.type.assert_not_called()


@pytest.mark.parametrize('char,keycode', [('A', 0), ('!', 18)])
def test_macos_type_char_shifted_holds_shift(fake_pynput, char_map, char,
                                            keycode):
    kb = MagicMock()
    c2k.macos_type_char(kb, fake_pynput, char)
    fake_pynput.KeyCode.from_vk.assert_called_once_with(keycode)
    kb.pressed.assert_called_once_with(fake_pynput.Key.shift)
    key = fake_pynput.KeyCode.from_vk.return_value
    kb.press.assert_called_once_with(key)
    kb.release.assert_called_once_with(key)
    kb.type.assert_not_called()


@pytest.mark.parametrize('char', ['\n', '\t', '\u00e9', '\U0001f600'])
def test_macos_type_char_falls_back_to_unicode(fake_pynput, char_map, char):
    kb = MagicMock()
    c2k.macos_type_char(kb, fake_pynput, char)
    kb.type.assert_called_once_with(char)
    kb.press.assert_not_called()


def test_macos_char_map_built_once(fake_pynput):
    with patch.object(c2k, '_macos_char_map', None), \
            patch.object(c2k, 'build_macos_char_map',
                         return_value=dict(CHAR_MAP)) as build:
        c2k.macos_type_char(MagicMock(), fake_pynput, 'a')
        c2k.macos_type_char(MagicMock(), fake_pynput, 'A')
    build.assert_called_once_with()


def test_build_macos_char_map_prefers_unshifted():
    layout = {(0, 0): 'a', (0, 2): 'A', (1, 0): '1', (1, 2): '!',
              (2, 0): 'x', (2, 2): 'x', (3, 0): '\r', (3, 2): '\r'}
    darwin = MagicMock()
    darwin.keycode_to_string.side_effect = \
        lambda _ctx, kc, mod=0: layout.get((kc, mod), '')
    with patch.dict(sys.modules, {'pynput': MagicMock(),
                                  'pynput._util': MagicMock(),
                                  'pynput._util.darwin': darwin}):
        mapping = c2k.build_macos_char_map()
    assert mapping == {'a': (0, False), 'A': (0, True), '1': (1, False),
                       '!': (1, True), 'x': (2, False)}


# --- waiting for modifier release -------------------------------------------

# The autouse fixture patches the module attribute; keep the original.
_ORIGINAL_WAIT = c2k.wait_for_modifier_release


@patch.object(c2k.time, 'sleep')
def test_wait_for_modifier_release_polls_until_released(mock_sleep):
    with patch.object(c2k, 'IS_MACOS', True), \
            patch.object(c2k, 'macos_modifiers_held',
                         side_effect=[True, True, False]) as held:
        _ORIGINAL_WAIT(timeout=5)
    assert held.call_count == 3
    assert mock_sleep.call_count == 2


@patch.object(c2k.time, 'sleep')
def test_wait_for_modifier_release_gives_up_after_timeout(mock_sleep):
    with patch.object(c2k, 'IS_MACOS', True), \
            patch.object(c2k, 'macos_modifiers_held', return_value=True), \
            patch.object(c2k.time, 'monotonic', side_effect=[0, 1, 3]):
        _ORIGINAL_WAIT(timeout=2)
    assert mock_sleep.call_count == 1


def test_wait_for_modifier_release_noop_off_macos():
    with patch.object(c2k, 'IS_MACOS', False), \
            patch.object(c2k, 'macos_modifiers_held') as held:
        _ORIGINAL_WAIT()
    held.assert_not_called()


@patch.object(c2k, 'type_text')
@patch.object(c2k, 'pyperclip')
def test_send_clipboard_waits_for_modifiers_before_typing(mock_pyperclip,
                                                          mock_type_text):
    order = []
    with patch.object(c2k, 'wait_for_modifier_release',
                      side_effect=lambda: order.append('wait')):
        mock_type_text.side_effect = lambda *a: order.append('type')
        c2k.send_clipboard()
    assert order == ['wait', 'type']


# --- hotkey runs typing off the listener thread ------------------------------

def test_on_hotkey_types_on_worker_thread():
    done = threading.Event()
    seen = {}

    def fake_send():
        seen['thread'] = threading.current_thread()
        done.set()

    with patch.object(c2k, 'send_clipboard', side_effect=fake_send):
        c2k.on_hotkey()
        assert done.wait(2)
    assert seen['thread'] is not threading.current_thread()


def test_on_hotkey_ignores_presses_while_typing():
    release = threading.Event()
    started = threading.Event()
    calls = []

    def slow_send():
        calls.append(1)
        started.set()
        release.wait(2)

    with patch.object(c2k, 'send_clipboard', side_effect=slow_send):
        c2k.on_hotkey()
        assert started.wait(2)
        c2k.on_hotkey()  # ignored: previous paste still running
        release.set()
        for _ in range(200):
            if not c2k._send_lock.locked():
                break
            threading.Event().wait(0.01)
    assert calls == [1]
    assert not c2k._send_lock.locked()


@pytest.mark.filterwarnings(
    'ignore::pytest.PytestUnhandledThreadExceptionWarning')
def test_on_hotkey_releases_lock_after_failure():
    done = threading.Event()

    def failing_send():
        done.set()
        raise RuntimeError('boom')

    with patch.object(c2k, 'send_clipboard', side_effect=failing_send):
        c2k.on_hotkey()
        assert done.wait(2)
        for _ in range(200):
            if not c2k._send_lock.locked():
                break
            threading.Event().wait(0.01)
    assert not c2k._send_lock.locked()
