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

// Clicking the toolbar icon types too. Options are on the icon's right-click
// menu (Chrome adds it for options_page).
chrome.action.onClicked.addListener((tab) => typeClipboard(tab));

async function typeClipboard(tab) {
  if (!tab || tab.id === undefined) return;
  try {
    const { delayMs } = await chrome.storage.sync.get(DEFAULTS);
    const text = await readClipboard();
    if (!text) return flash(tab.id, 'empty');

    const result = await injectAndType(tab.id, text, delayMs);
    flash(tab.id, result.status);
  } catch (err) {
    // chrome://, edge://, the web store and PDF viewer refuse scripts.
    flash(tab.id, 'error', `Cannot type on this page: ${err.message}`);
  }
}

async function injectAndType(tabId, text, delayMs) {
  // Login forms often live in iframes, so look at every frame. Frames we may
  // not script make the whole call fail; fall back to the top frame alone.
  let probes;
  let target;
  for (target of [{ tabId, allFrames: true }, { tabId }]) {
    try {
      await chrome.scripting.executeScript({ target, files: ['typer.js'] });
      probes = await chrome.scripting.executeScript({
        target, func: () => globalThis.c2kProbe(),
      });
      break;
    } catch (err) {
      if (target.allFrames === undefined) throw err;
    }
  }

  const frameId = pickFrame(probes);
  if (frameId === undefined) return { status: 'no-field' };
  const [{ result }] = await chrome.scripting.executeScript({
    target: { tabId, frameIds: [frameId] },
    func: (t, d) => globalThis.c2kTypeText(t, d),
    args: [text, delayMs],
  });
  return result;
}

// Type into exactly one frame. Prefer the frame that has focus (the keyboard
// shortcut). After a toolbar click no frame may have focus, so take the frame
// whose last-focused element is a field; prefer an iframe, because the top
// frame's remembered element is usually the <iframe> holding the form.
function pickFrame(probes) {
  const editable = probes.filter((p) => p.result && p.result.editable);
  const focused = editable.find((p) => p.result.focused);
  if (focused) return focused.frameId;
  if (probes.some((p) => p.result && p.result.focused)) return undefined;
  const sub = editable.find((p) => p.frameId !== 0);
  return (sub || editable[0] || {}).frameId;
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
