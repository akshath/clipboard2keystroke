# Store listing: Chrome Web Store, Edge Add-ons and Firefox Add-ons

Text and files to paste into the Chrome Web Store Developer Dashboard
(https://chrome.google.com/webstore/devconsole) and Microsoft Partner Center
(https://partner.microsoft.com/dashboard/microsoftedge), and Firefox
Add-ons (https://addons.mozilla.org/developers/).

## Before each upload

1. Raise `version` in `extension/manifest.json`. The store rejects a version
   it has already seen.
2. Run `./package.sh` to build `dist/clipboard2keystroke-<version>.zip`.
3. If the settings page or logo changed, run `store/render.sh` to refresh the
   images.
4. Upload the zip: **Package › Upload new package**.

## Store listing tab

**Name** (from the manifest): Clipboard2Keystroke

**Summary** (from the manifest's `description`, max 132 characters):
Type the clipboard into the focused field of a web page, one character at a time, for sites that block paste.

**Description:**

```
Paste blocked? Clipboard2Keystroke types it for you.

Some login pages, bank sites and admin consoles block pasting into password and text fields. Clipboard2Keystroke reads your clipboard and types it into the field one character at a time, just like you would.

HOW TO USE IT
1. Copy the text, such as a password from your password manager.
2. Click into the field on the page.
3. Click the Clipboard2Keystroke icon, or press Alt+Shift+K (Option+Shift+K on Mac).

FEATURES
• Works in password fields, text boxes and rich text editors, including fields inside embedded login frames.
• Adjustable typing speed: instant, fast, normal or careful, or any delay you choose.
• Stops typing at once if you click somewhere else, so text never lands in the wrong place.
• Skips line breaks in single-line fields, so a copied password never submits a form by accident.
• The toolbar badge shows the result: OK, no field selected, stopped, or page not supported.
• Works on Mac even when macOS Secure Input blocks other typing tools.

PRIVACY
Your clipboard is read only when you click the icon or press the shortcut. Nothing is stored, logged or sent anywhere. The extension makes no network requests.

Open source: https://github.com/akshath/clipboard2keystroke
```

**Category:** Productivity (Edge: Productivity)

**Language:** English

**Graphic assets** (all in `store/`):

| Field | File | Size |
|---|---|---|
| Store icon | `extension/icons/icon128.png` | 128×128 |
| Screenshot 1 | `store/screenshot-1-login.png` | 1280×800 |
| Screenshot 2 | `store/screenshot-2-settings.png` | 1280×800 |
| Small promo tile | `store/promo-small-440x280.png` | 440×280 |
| Marquee promo tile (optional) | `store/promo-marquee-1400x560.png` | 1400×560 |

**Homepage URL:** https://github.com/akshath/clipboard2keystroke

**Support URL:** https://github.com/akshath/clipboard2keystroke/issues

## Privacy tab

**Single purpose description:**

```
Types the clipboard text into the field the user selected on the current web page, one character at a time, for pages that block pasting.
```

**Permission justifications:**

| Permission | Justification |
|---|---|
| `clipboardRead` | Reads the clipboard text to type. This happens only when the user clicks the toolbar icon or presses the extension's shortcut. The text is typed into the page and then discarded. |
| `activeTab` | Gives access to the current tab only when the user clicks the icon or presses the shortcut, so the extension can type into the field they selected. No other tabs are accessed. |
| `scripting` | Injects the small script that types the text into the selected field of the current tab, including fields inside login frames. It runs only when the user triggers it. |
| `offscreen` | Extension service workers cannot read the clipboard, so a hidden offscreen document reads it and is closed straight away. |
| `storage` | Saves the user's typing speed setting. |

**Remote code:** No, I am not using remote code. All code is in the package.

**Data usage.** Leave every data type unticked: the extension does not
collect or transmit any user data. The clipboard and page are handled only on
the device, at the user's request. Then tick all three certifications:

- I do not sell or transfer user data to third parties, outside of the approved use cases.
- I do not use or transfer user data for purposes that are unrelated to my item's single purpose.
- I do not use or transfer user data to determine creditworthiness or for lending purposes.

If a reviewer asks you to declare the clipboard contents anyway, tick
**Authentication information** and **Website content**, and say that both are
processed locally only.

**Privacy policy URL:**
https://github.com/akshath/clipboard2keystroke/blob/main/PRIVACY.md

## Distribution tab

- **Visibility:** Public (or Unlisted to share by link only).
- **Regions:** All regions.

## Edge Add-ons

Partner Center takes the same zip, description, images and privacy policy
URL. Edge doesn't ask for per-permission justifications in the same form; if
it asks for notes for certification, paste the permission table above.

## Firefox Add-ons (AMO)

The same zip works. Fields on addons.mozilla.org:

| Field | Value |
|---|---|
| Name | Clipboard2Keystroke (from the manifest) |
| Add-on URL | `clipboard2keystroke` |
| Summary (max 250 characters) | the manifest `description` above |
| Description | the same description as Chrome. AMO accepts Markdown, so the bullets can stay. |
| Categories | Other (AMO has no Productivity category) |
| Support email or website | https://github.com/akshath/clipboard2keystroke/issues |
| License | MIT License |
| Privacy policy | paste the text of `PRIVACY.md` (AMO takes the text, not a link) |
| Icon | `extension/icons/icon128.png` (taken from the package) |
| Screenshots | `store/screenshot-1-login.png`, `store/screenshot-2-settings.png` |
| Source code | Not needed: the code isn't minified, bundled or generated. |

The data-collection answer comes from the manifest
(`data_collection_permissions: none`), so AMO shows "no data collected".

**Notes to reviewer:**

```
The extension reads the clipboard only when the user clicks the toolbar icon or presses Alt+Shift+K, then types it into the field the user selected on the current tab (activeTab + scripting). Nothing is stored except the typing-speed setting, and there are no network requests. The "offscreen" permission and offscreen.html/offscreen.js are used only by Chrome; Firefox reads the clipboard directly from the background page. To test: copy some text, click into any text field, then click the toolbar icon.
```
