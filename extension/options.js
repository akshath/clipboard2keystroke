const DEFAULTS = { delayMs: 100 };
const SAMPLE = 'Hunter2-Sample!';

const delayInput = document.getElementById('delay');
const delayLabel = document.getElementById('delay-label');
const presets = [...document.querySelectorAll('.preset')];
const saved = document.getElementById('saved');
const testField = document.getElementById('test-field');
const typeButton = document.getElementById('type-sample');

document.getElementById('version').textContent =
  `v${chrome.runtime.getManifest().version}`;

// --- Typing speed ---------------------------------------------------------

function showDelay(delayMs) {
  delayInput.value = delayMs;
  delayLabel.textContent = delayMs === 0 ? 'Instant' : `${delayMs} ms`;
  for (const button of presets) {
    button.setAttribute('aria-pressed', String(Number(button.dataset.ms) === delayMs));
  }
}

let savedTimer;
async function saveDelay(delayMs) {
  delayMs = Math.max(0, Math.round(Number(delayMs) || 0));
  showDelay(delayMs);
  await chrome.storage.sync.set({ delayMs });
  saved.hidden = false;
  clearTimeout(savedTimer);
  savedTimer = setTimeout(() => { saved.hidden = true; }, 1500);
}

chrome.storage.sync.get(DEFAULTS).then(({ delayMs }) => showDelay(delayMs));

// 'input' updates the label while dragging; 'change' saves once on release.
delayInput.addEventListener('input', () => showDelay(Number(delayInput.value)));
delayInput.addEventListener('change', () => saveDelay(delayInput.value));
for (const button of presets) {
  button.addEventListener('click', () => saveDelay(button.dataset.ms));
}

// --- Shortcut -------------------------------------------------------------

// macOS reports shortcuts as symbols ("⌥⇧K"), other platforms as "Alt+Shift+K".
const KEY_NAMES = { '⌥': '⌥ Option', '⇧': '⇧ Shift', '⌘': '⌘ Command', '⌃': '⌃ Control' };

function shortcutKeys(shortcut) {
  if (!shortcut) return [];
  if (shortcut.includes('+')) return shortcut.split('+');
  return [...shortcut].map((ch) => KEY_NAMES[ch] || ch);
}

chrome.commands.getAll().then((commands) => {
  const command = commands.find((c) => c.name === 'type-clipboard');
  const keys = shortcutKeys(command && command.shortcut);
  const box = document.getElementById('shortcut');
  if (keys.length === 0) {
    box.textContent = 'Not set';
    return;
  }
  keys.forEach((key, i) => {
    if (i > 0) {
      const plus = document.createElement('span');
      plus.textContent = '+';
      plus.setAttribute('aria-hidden', 'true');
      box.append(plus);
    }
    const kbd = document.createElement('kbd');
    kbd.textContent = key;
    box.append(kbd);
  });
});

// Pages cannot link to chrome:// URLs; open it through the tabs API. Edge
// redirects chrome://extensions to edge://extensions.
document.getElementById('change-shortcut').addEventListener('click', () => {
  chrome.tabs.create({ url: 'chrome://extensions/shortcuts' });
});

// --- Try it ---------------------------------------------------------------

// Uses the same typer.js the extension injects into pages, so this shows the
// real speed and behaviour.
typeButton.addEventListener('click', async () => {
  typeButton.disabled = true;
  testField.value = '';
  testField.focus();
  try {
    await globalThis.c2kTypeText(SAMPLE, Number(delayInput.value));
  } finally {
    typeButton.disabled = false;
  }
});
