const DEFAULTS = { delayMs: 100 };

const delayInput = document.getElementById('delay');
const saved = document.getElementById('saved');

chrome.storage.sync.get(DEFAULTS).then(({ delayMs }) => {
  delayInput.value = delayMs;
});

delayInput.addEventListener('change', async () => {
  const delayMs = Math.max(0, Number(delayInput.value) || 0);
  delayInput.value = delayMs;
  await chrome.storage.sync.set({ delayMs });
  saved.textContent = 'Saved';
  setTimeout(() => { saved.textContent = ''; }, 1500);
});

chrome.commands.getAll().then((commands) => {
  const command = commands.find((c) => c.name === 'type-clipboard');
  document.getElementById('shortcut').textContent =
    (command && command.shortcut) || 'not set';
});

// Pages cannot link to chrome:// URLs; open it through the tabs API. Edge
// redirects chrome://extensions to edge://extensions.
document.getElementById('change-shortcut').addEventListener('click', (e) => {
  e.preventDefault();
  chrome.tabs.create({ url: 'chrome://extensions/shortcuts' });
});
