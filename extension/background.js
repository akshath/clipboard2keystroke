// Service worker: on the keyboard shortcut, read the clipboard and type it
// into the focused field of the active tab.
//
// The shortcut is handled by the browser itself, so it keeps working while
// macOS Secure Input is on (e.g. a password field has focus), which hides
// keystrokes from the desktop clipboard2keystroke.py script.

const DEFAULTS = { delayMs: 100 };

const MESSAGES = {
  'no-field': 'Click into a text or password field first.',
  'busy': 'Still typing the previous clipboard.',
  'empty': 'The clipboard has no text.',
};

chrome.commands.onCommand.addListener((command, tab) => {
  if (command === 'type-clipboard') typeClipboard(tab);
});

chrome.action.onClicked.addListener(() => chrome.runtime.openOptionsPage());

async function typeClipboard(tab) {
  if (!tab || tab.id === undefined) return;
  try {
    const { delayMs } = await chrome.storage.sync.get(DEFAULTS);
    const text = await readClipboard();
    if (!text) return flash(tab.id, 'empty');

    const results = await injectAndType(tab.id, text, delayMs);
    const statuses = results.map((r) => r && r.result && r.result.status);
    // Only the focused frame types; every other frame reports 'no-focus'.
    for (const status of ['typed', 'stopped', 'busy', 'no-field']) {
      if (statuses.includes(status)) return flash(tab.id, status);
    }
    flash(tab.id, 'no-field');
  } catch (err) {
    // chrome://, edge://, the web store and PDF viewer refuse scripts.
    flash(tab.id, 'error', `Cannot type on this page: ${err.message}`);
  }
}

async function injectAndType(tabId, text, delayMs) {
  // Login forms often live in iframes, so try every frame. Frames we may not
  // script make the whole call fail; fall back to the top frame alone.
  for (const target of [{ tabId, allFrames: true }, { tabId }]) {
    try {
      await chrome.scripting.executeScript({ target, files: ['typer.js'] });
      return await chrome.scripting.executeScript({
        target,
        func: (t, d) => globalThis.c2kTypeText(t, d),
        args: [text, delayMs],
      });
    } catch (err) {
      if (target.allFrames === undefined) throw err;
    }
  }
}

// Service workers have no DOM, so the clipboard is read in an offscreen
// document (see offscreen.js).
async function readClipboard() {
  const existing = await chrome.runtime.getContexts({
    contextTypes: ['OFFSCREEN_DOCUMENT'],
  });
  if (existing.length === 0) {
    await chrome.offscreen.createDocument({
      url: 'offscreen.html',
      reasons: ['CLIPBOARD'],
      justification: 'Read the clipboard text to type it into the page.',
    });
  }
  try {
    return await chrome.runtime.sendMessage({
      target: 'offscreen', type: 'read-clipboard',
    });
  } finally {
    // Do not keep a document around that holds the clipboard contents.
    await chrome.offscreen.closeDocument().catch(() => {});
  }
}

// Short feedback on the toolbar icon: badge plus a tooltip explaining it.
async function flash(tabId, status, detail) {
  const badge = {
    typed: ['OK', '#188038'], stopped: ['STOP', '#e37400'],
    busy: ['…', '#e37400'], empty: ['0', '#e37400'],
    'no-field': ['?', '#e37400'], error: ['ERR', '#d93025'],
  }[status] || ['?', '#d93025'];
  const title = detail || MESSAGES[status] ||
    (status === 'stopped' ? 'Stopped: focus left the field.' : '');
  await chrome.action.setBadgeBackgroundColor({ tabId, color: badge[1] });
  await chrome.action.setBadgeText({ tabId, text: badge[0] });
  if (title) await chrome.action.setTitle({ tabId, title });
  setTimeout(() => {
    chrome.action.setBadgeText({ tabId, text: '' }).catch(() => {});
    chrome.action.setTitle({
      tabId, title: chrome.runtime.getManifest().action.default_title,
    }).catch(() => {});
  }, 4000);
}
