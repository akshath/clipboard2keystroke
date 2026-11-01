# How to publish the extension

Step-by-step guide to publishing Clipboard2Keystroke on the Chrome Web Store
and Microsoft Edge Add-ons, and to releasing updates later.

The text to paste into the store forms is in
[`STORE_LISTING.md`](STORE_LISTING.md). This guide says where it goes.

Store dashboards change their layout from time to time. If a button named
here has moved, look for the same field name nearby.

---

## 1. Before you start

You need:

- A Google account for the Chrome Web Store, with
  [2-step verification](https://myaccount.google.com/signinoptions/two-step-verification)
  turned on (the dashboard requires it).
- A Microsoft account for Edge Add-ons (optional).
- Chrome installed, to render the images.
- `zip` on your path (built into macOS and most Linux systems).

Check the extension works before you package it:

1. Load it unpacked from `extension/` (`chrome://extensions` › **Developer mode**
   › **Load unpacked**).
2. Try it on a real login page, with both the toolbar icon and the shortcut.
3. Open the settings page (right-click the icon › **Options**) and try the
   **Try it** field.
4. Run the typing tests (see the README's **Testing** section).

## 2. Build the package

From the repo root:

```bash
./package.sh
```

This writes `dist/clipboard2keystroke-<version>.zip`, with `manifest.json` at
the top level. The version comes from `extension/manifest.json`.

If the logo or the settings page changed since the images were made, refresh
them too:

```bash
store/render.sh
```

Look through the four images in `store/` before uploading them.

## 3. Chrome Web Store: first release

### 3.1 Register as a developer (one time)

1. Open the
   [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole)
   and sign in.
2. Accept the developer agreement and pay the one-time US$5 registration fee.
3. In **Account**, set the publisher name shown on the listing, and verify your
   contact email. You can't publish until the email is verified.

### 3.2 Create the item

1. Click **New item** and upload `dist/clipboard2keystroke-<version>.zip`.
2. The dashboard opens the new draft. Its name, summary and icon come from
   the manifest.

### 3.3 Store listing tab

Copy each field from the **Store listing tab** section of `STORE_LISTING.md`:

- **Description**
- **Category:** Productivity
- **Language:** English
- **Store icon:** `extension/icons/icon128.png`
- **Screenshots:** `store/screenshot-1-login.png`, then
  `store/screenshot-2-settings.png`
- **Small promo tile:** `store/promo-small-440x280.png`
- **Marquee promo tile:** `store/promo-marquee-1400x560.png` (optional)
- **Homepage URL** and **Support URL**

Click **Save draft**.

### 3.4 Privacy tab

This tab decides how smoothly the review goes. Copy from the **Privacy tab**
section of `STORE_LISTING.md`:

1. **Single purpose description.**
2. **Permission justification** for each permission: `clipboardRead`,
   `activeTab`, `scripting`, `offscreen` and `storage`.
3. **Remote code:** No.
4. **Data usage:** leave every data type unticked, then tick all three
   certifications.
5. **Privacy policy URL:**
   `https://github.com/akshath/clipboard2keystroke/blob/main/PRIVACY.md`

Click **Save draft**.

### 3.5 Distribution tab

- **Visibility:** **Public** to appear in search, or **Unlisted** so only
  people with the link can install it. Unlisted is a good choice for a first
  release you want to try out before announcing it.
- **Regions:** all regions.

### 3.6 Submit

1. Click **Submit for review**.
2. You can choose to publish automatically once approved, or to publish
   yourself after approval. Publishing yourself lets you pick the moment.
3. Review usually takes from a few days to a couple of weeks. Extensions that
   read the clipboard can take longer. The dashboard shows the status, and
   Google emails you the result.

When it's approved, copy the listing link from the dashboard. It looks like
`https://chromewebstore.google.com/detail/<id>`. Add it to the README's
**Browser extension** section and the GitHub **About** box.

## 4. Edge Add-ons (optional)

Edge has its own store. Registration is free.

1. Open
   [Partner Center › Edge](https://partner.microsoft.com/dashboard/microsoftedge)
   and register as a developer.
2. Click **Create new extension** and upload the same zip.
3. **Availability:** Public or Hidden, and all markets.
4. **Properties:** category Productivity, privacy policy URL, website and
   support URLs from `STORE_LISTING.md`.
5. **Store listings:** add English. Paste the description and add the same
   icon, screenshots and promo tiles.
6. **Submit.** In **Notes for certification**, paste the permission table from
   `STORE_LISTING.md`, so the reviewer knows why each permission is needed.

Edge reviews typically take up to a week.

## 5. Releasing an update

1. Make and merge the change as usual (branch and pull request).
2. Raise `version` in `extension/manifest.json`, for example `1.0.0` to
   `1.0.1`. Both stores reject a version they've seen before.
3. Run `./package.sh` (and `store/render.sh` if the visuals changed).
4. **Chrome:** open the item in the dashboard, go to **Package**, click
   **Upload new package**, then **Submit for review**.
   **Edge:** open the extension in Partner Center, choose **Update**, upload
   the zip, then **Publish**.
5. If you changed permissions or how data is handled, update
   `PRIVACY.md`, `STORE_LISTING.md` and the store's **Privacy** tab in the
   same release.

Users get the update automatically within a few hours of approval.

Adding a new permission makes the browser disable the extension until each
user accepts the new permission, so only add one when it's really needed.

## 6. If the review is rejected

The rejection email names the policy and usually what to change. Common ones
for this kind of extension:

| Rejection | What to do |
|---|---|
| **Excessive permissions** | Re-check each permission justification is specific about when it's used. Every permission listed must actually be used. |
| **Missing or inadequate privacy policy** | Make sure the URL opens `PRIVACY.md` publicly, and that it mentions the clipboard. |
| **Data usage disclosure doesn't match** | The reviewer may want the clipboard declared. Tick **Authentication information** and **Website content**, and keep the note that both are handled locally only. |
| **Unclear single purpose or description** | Make the description start with the one thing it does: typing the clipboard into a field on pages that block paste. |
| **Screenshot shows a brand you don't own** | Only use the made-up `login.example.com` page, never a real site's login screen. |

Fix it, raise the version if you changed the package, and submit again. You
can also reply to the email or use the dashboard's appeal link if you think
the reviewer misread something.
