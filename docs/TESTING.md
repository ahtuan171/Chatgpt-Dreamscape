# Testing Dreamscape

The fast smoke test loads `tests/chatgpt-fixture.html` (a **simulated** ChatGPT DOM) and injects the bundled userscript. It checks:

- Conversation and sidebar remain visible
- All three built-in wallpapers switch, display previews, and preserve dimming/position controls
- Victor is visible near the right corner of the composer, an additional 15% larger (74 × 59 CSS px), moves left then turns to face right within an 80px patrol, and can be disabled
- The outer composer **dock** remains transparent for collapsed and expanded composers; the rounded input defaults to translucent glass (58% charcoal), with an optional solid-background toggle
- Attachment-style composer reparenting with the **same form element**, 12 newly opaque nested dock wrappers, and a separate decorative black backdrop: all become transparent without touching conversation text (CSS and screenshot-pixel regression)
- The Victor, animation, translucent-composer and Dreamscape controls are accessible, visible checkboxes, and the glass setting persists
- Custom wallpaper import, IndexedDB storage, restore and deletion
- Saved selections of removed built-in wallpapers safely fall back to Moonlit Castle, without deleting custom uploads
- Fallback selection of alternate composer markup

Run from repository root:

```bash
node tools/build.mjs
python -m pip install playwright pillow
python -m playwright install chromium
python tests/test_browser.py
```

Tests try a loopback fixture server (real IndexedDB/localStorage). Restricted sandboxes may prohibit browser navigation. In that case tests use an `about:blank` fixture with in-memory storage shims; the report clearly distinguishes simulated storage checks from native IndexedDB persistence.

**Before a release**, manually verify the userscript in authenticated desktop Chrome and Firefox (and Edge/Brave when practical), including a long conversation, collapsed/expanded sidebar, empty chat, sending a message, composer resizing, wallpaper upload, page reload, and disabling the script. These cannot be guaranteed from a fixture alone.

### Wallpaper readability and licensing

All three built-in wallpapers use light chat text over dark backgrounds. Because every display/browser renders contrast differently, manually verify each wallpaper with real ChatGPT messages and headings. Third-party photos and fan art are **not bundled** without distribution permission; users may import their own privately.
