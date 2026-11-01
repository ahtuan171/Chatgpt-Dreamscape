# Testing Dreamscape

The fast smoke test loads `tests/chatgpt-fixture.html` (a **simulated** ChatGPT DOM) and injects the bundled userscript. It checks:

- Conversation and sidebar remain visible
- All 10 original wallpapers switch, display previews, and preserve dimming/position controls
- Victor is visible on the left edge of the composer, moves within a short 80px patrol, and can be disabled
- Black background on the composer **dock** disappears but the rounded composer remains opaque
- Custom wallpaper import, IndexedDB storage, restore and deletion
- Fallback selection of alternate composer markup

Run from repository root:

```bash
node tools/build.mjs
python -m pip install playwright
python -m playwright install chromium
python tests/test_browser.py
```

Tests try a loopback fixture server (real IndexedDB/localStorage). Restricted sandboxes may prohibit browser navigation. In that case tests use an `about:blank` fixture with in-memory storage shims; the report clearly distinguishes simulated storage checks from native IndexedDB persistence.

**Before a release**, manually verify the userscript in authenticated desktop Chrome and Firefox (and Edge/Brave when practical), including a long conversation, collapsed/expanded sidebar, empty chat, sending a message, composer resizing, wallpaper upload, page reload, and disabling the script. These cannot be guaranteed from a fixture alone.

### Wallpaper readability and licensing

The original wallpaper set was curated for dark reading surfaces; central regions have low average luminance. Because every display/browser renders contrast differently, manually verify each wallpaper with real ChatGPT messages and headings. Third-party photos and fan art are **not bundled** without distribution permission; users may import their own privately.
