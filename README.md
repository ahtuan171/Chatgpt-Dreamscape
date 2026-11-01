# ☾ ChatGPT Dreamscape

**Make your ChatGPT feel like home.** Dreamscape is an independent, open-source userscript that adds atmospheric wallpapers and **Victor**, a tiny gray pixel cat, to the desktop ChatGPT web interface.

> **Early public preview · v0.3.1.** This is a community customization, not an official OpenAI/ChatGPT feature. ChatGPT's page structure can change; if you spot an issue, please open a GitHub issue.

## ✨ Features

- **3 built-in wallpapers**: Moonlit Castle, Midnight Tulips, and Prince & Princess. All three use light chat text over dark atmospheric artwork.
- **Your own wallpapers**: import PNG, JPEG or WebP; image processing and storage happen *in your browser* via IndexedDB.
- **Personal controls**: wallpaper previews, per-wallpaper darkening and horizontal cropping (0% left / 50% center / 100% right when cropped).
- **Victor**: the gray pixel cat stays near the **upper-right corner of the composer**, is about 10% larger, walks a short distance toward the center (up to 80px), turns to face back before returning, rests, blinks, and sleeps. Turn him off at any time.
- **Lightweight, optional styling**: the sidebar stays readable; the composer stays dark on the three built-in themes. A toggle restores ChatGPT's default styling.
- **Privacy-first**: no analytics, no external image uploads, no chat-message collection, no account access beyond the web page needed for styling.

## 🚀 Install (desktop only; no terminal)

1. Install a userscript manager such as [Tampermonkey](https://www.tampermonkey.net/) or [Violentmonkey](https://violentmonkey.github.io/) in your desktop browser.
2. **[Install ChatGPT Dreamscape](https://github.com/ahtuan171/Chatgpt-Dreamscape/raw/refs/heads/main/dist/dreamscape.user.js)** — click **Install** when the userscript manager prompts you.
3. Open or refresh [ChatGPT](https://chatgpt.com/). Click **☾** at the lower-right corner to choose a wallpaper, upload your own, and toggle Victor.

If the browser downloads the `.user.js` file instead of opening the installer, open the file with your userscript manager or import it from the manager's dashboard. Some Chromium-based browsers require allowing user scripts in extension settings. You do **not** need to clone the repository, install Node.js or use a terminal.

**Compatibility targets:** Chrome, Firefox, Edge and Brave on Windows, macOS and Linux. Chrome/Firefox get priority testing. Mobile browsers and desktop-app injection are intentionally out of scope; cross-platform behavior is a target, not a promise of verified support on every release.

## 🖼️ Bring your own wallpaper

**Updating from an earlier Dreamscape version?** Retired built-in wallpapers are no longer included. If one was selected, Dreamscape will switch to Moonlit Castle automatically. Wallpapers you imported into **My Wallpapers** remain stored locally in your browser.

Choose **☾ → Add wallpaper**. Files must be PNG/JPEG/WebP and under 15 MB. Dreamscape resizes large images (up to 2400 × 1600) and converts them to optimized WebP in your browser, then saves them locally to IndexedDB. You can select, dim, reposition or delete imported wallpapers. Nothing is sent to a wallpaper server.

Imported images and preferences belong to the specific browser profile and website origin, and won't sync across computers automatically. Browsers may clear local data. Only upload art you have the right to use; importing it does **not** publish it to this repository.

## 🐈 Meet Victor

Victor is the **only** bundled pet. He starts near the right corner of the message box, patrols a short stretch facing the direction of travel, and rests between movements. His animations are quiet, optional and respect your system's reduced-motion preference. The personal red Spidey sprite is **not included** in the public version. Previous users should disable all old Dreamscape scripts to avoid clashes.

## 🛠️ For contributors

You don't need this section to use Dreamscape. To develop locally:

```bash
git clone https://github.com/ahtuan171/Chatgpt-Dreamscape.git
cd Chatgpt-Dreamscape
node tools/build.mjs
python -m pip install playwright
python -m playwright install chromium
python tests/test_browser.py
```

Source code lives in `src/`, bundled original art in `assets/`, build tooling in `tools/`, and the installable userscript in `dist/dreamscape.user.js`. Build output embeds the included images, so installed users make **no external wallpaper requests**. The browser test uses a local fixture, not a real ChatGPT login; see [Testing](docs/TESTING.md).

## 🛡️ Safety and limitations

- Run Dreamscape only on `https://chatgpt.com/*` and review userscript permissions before installation.
- It does not read or transmit conversation text; the typing listener only detects activity on the composer, without storing content.
- ChatGPT UI changes can temporarily break pet positioning or visual styles. Disable Dreamscape in the userscript manager if anything looks wrong, and [report the issue](https://github.com/ahtuan171/Chatgpt-Dreamscape/issues).
- Built-in assets have separate attribution terms; see [Artwork](ASSETS.md). Do not redistribute third-party imagery without permission.

## License

Source code: [MIT License](LICENSE). Original art and Victor sprites: see [ASSETS.md](ASSETS.md).
