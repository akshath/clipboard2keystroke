// Offscreen document: reads the clipboard for the service worker.
//
// navigator.clipboard.readText() needs a focused document, which an offscreen
// document never is. execCommand('paste') into a textarea works instead,
// because the extension holds the clipboardRead permission.

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.target !== 'offscreen' || message.type !== 'read-clipboard') {
    return false;
  }
  const area = document.getElementById('clipboard');
  area.value = '';
  area.focus();
  document.execCommand('paste');
  const text = area.value;
  area.value = '';
  sendResponse(text);
  return false;
});
