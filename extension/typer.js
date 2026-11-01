// Injected into every frame of the active tab. Defines c2kProbe() and
// c2kTypeText(text, delayMs), which types `text` into the focused field of this frame one
// character at a time. Kept free of extension APIs so it can be tested in a
// plain page (see test/typer-test.html).
(() => {
  if (globalThis.c2kTypeText) return;

  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  // Input types that hold free text; others (checkbox, date, ...) are skipped.
  const TEXT_INPUT_TYPES = new Set(
    ['text', 'password', 'email', 'search', 'tel', 'url', 'number']);

  // document.activeElement stops at shadow hosts; walk into open shadow roots.
  function deepActiveElement(doc) {
    let el = doc.activeElement;
    while (el && el.shadowRoot && el.shadowRoot.activeElement) {
      el = el.shadowRoot.activeElement;
    }
    return el;
  }

  // 'single' (no newlines), 'multi' (textarea), 'rich' (contenteditable) or
  // null when the element does not take typed text.
  function fieldKind(el) {
    if (!el || el.disabled || el.readOnly) return null;
    if (el.isContentEditable) return 'rich';
    if (el.tagName === 'TEXTAREA') return 'multi';
    if (el.tagName === 'INPUT' && TEXT_INPUT_TYPES.has(el.type)) return 'single';
    return null;
  }

  function dispatchKey(el, type, key) {
    return el.dispatchEvent(new KeyboardEvent(type, {
      key, bubbles: true, cancelable: true, composed: true,
    }));
  }

  // Fallback for fields where execCommand refuses (some framework widgets):
  // set the value through the native setter so React & co. notice, then fire
  // the input event a real keystroke would.
  function setValueDirectly(el, ch) {
    const proto = el.tagName === 'TEXTAREA'
      ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
    const setter = Object.getOwnPropertyDescriptor(proto, 'value').set;
    const value = el.value;
    // selectionStart is null on types without a caret (email, number).
    const start = el.selectionStart ?? value.length;
    const end = el.selectionEnd ?? value.length;
    setter.call(el, value.slice(0, start) + ch + value.slice(end));
    if (el.selectionStart !== null) {
      el.setSelectionRange(start + ch.length, start + ch.length);
    }
    el.dispatchEvent(new InputEvent('input', {
      inputType: 'insertText', data: ch, bubbles: true, composed: true,
    }));
  }

  function insertChar(el, kind, ch) {
    // execCommand goes through the browser's own editing path: it fires
    // trusted beforeinput/input events and keeps undo history and the caret.
    if (document.execCommand('insertText', false, ch)) return;
    if (kind !== 'rich') setValueDirectly(el, ch);
  }

  function typeChar(el, kind, ch) {
    if (ch === '\r') return;
    // A single-line field cannot hold a newline. Skipping it also drops the
    // trailing newline that copying a password from a file often adds, and
    // never submits a form behind the user's back.
    if (ch === '\n' && kind === 'single') return;
    const key = ch === '\n' ? 'Enter' : ch;
    // Respect preventDefault on keydown, as a real keystroke would: input
    // masks cancel the event and insert the character themselves.
    if (dispatchKey(el, 'keydown', key)) {
      dispatchKey(el, 'keypress', key);
      insertChar(el, kind, ch);
    }
    dispatchKey(el, 'keyup', key);
  }

  let busy = false;

  // Reports whether this frame has a field to type into, so the service
  // worker can pick one frame. Clicking the toolbar icon can take focus away
  // from the page, but document.activeElement still remembers the field.
  globalThis.c2kProbe = () => ({
    focused: document.hasFocus(),
    editable: fieldKind(deepActiveElement(document)) !== null,
  });

  // Resolves to {status, typed}. status is 'typed', 'stopped' (focus moved
  // away mid-way), 'busy' or 'no-field' (the focused element does not take
  // text). Works whether or not the window has focus.
  globalThis.c2kTypeText = async (text, delayMs) => {
    if (busy) return { status: 'busy', typed: 0 };
    const el = deepActiveElement(document);
    const kind = fieldKind(el);
    if (!kind) return { status: 'no-field', typed: 0 };

    busy = true;
    let typed = 0;
    try {
      for (const ch of text) {  // for...of walks code points, not UTF-16 units
        // Stop if the user moved focus: never type the rest somewhere else.
        if (deepActiveElement(document) !== el) {
          return { status: 'stopped', typed };
        }
        typeChar(el, kind, ch);
        typed++;
        if (delayMs > 0) await sleep(delayMs);
      }
      return { status: 'typed', typed };
    } finally {
      busy = false;
    }
  };
})();
