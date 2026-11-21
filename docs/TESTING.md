# Testing Dreamscape

## Release scope — v0.3.17

GitHub Actions for [PR #4](https://github.com/ahtuan171/Chatgpt-Dreamscape/pull/4) passed on 21 November 2026. These are **simulated browser tests**, not a guarantee that Chat/Work is compatible with all signed-in accounts.

The November 2026 Chat/Work stage regression simulates a full-height, multiply painted layout with a compact left rail and a Chat/Work switcher, verifying that stage backgrounds become transparent while the composer, controls and rail remain painted, and toggling Dreamscape restores native backgrounds. The geometry fixture is inferred from the user screenshot; it is not a captured authenticated ChatGPT DOM.

The fast smoke test loads `tests/chatgpt-fixture.html` (a **simulated** ChatGPT DOM) and injects the bundled userscript. It checks:

- User-reported conversation ancestor chain with 20 layers, most `display: contents`: New Chat → long conversation → New Chat, pointer-events-none backdrop pixels, unchanged transcript, controls and theme disable/enable at 1680×543, 1174×612 and 1334×900. The original 0.3.15 build fails this regression because boxless wrappers consume its 18-ancestor limit. Outer paint layers are reconstructed; this is not a live authenticated-session test.
- Conversation and sidebar remain visible
- All five built-in wallpapers switch, display previews, and preserve dimming/position controls
- Victor is visible near the right corner of the composer, an additional 15% larger (74 × 59 CSS px), moves left then turns to face right within an 80px patrol, and can be disabled
- The outer composer **dock** remains transparent for collapsed and expanded composers; the rounded input retains a solid dark surface (no glass composer option)
- Actual debug-DOM 32px `from-surface` gradient under the transcript sticky spacer (separate from footer): all 32 pixel rows match the wallpaper, scroll controls survive, and disabling restores the fade
- Bottom-only gradient strips and border seams below the input: all 12 bottom screenshot rows match the wallpaper, and original styling returns when disabled
- Boxless `display: contents` wrappers in the actual footer ancestor chain, with a pointer-events-none backdrop outside those wrappers
- Attachment-style composer reparenting with the **same form element**, 12 newly opaque nested dock wrappers, and a separate decorative black backdrop: all become transparent without touching conversation text (CSS and screenshot-pixel regression)
- Unlabelled decorative dock backdrops with default pointer events, nested gradient/pseudo-element layers, preserved clickable controls, and restoring backgrounds when Dreamscape is disabled
- Full-width form wrappers with a nested `data-composer-surface` / `composer-background` input surface and in-flow backdrops; input editing and send control remain usable
- The Victor, animation and Dreamscape controls are accessible, visible checkboxes; the retired glass setting is no longer available
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

## Manual checklist before a release

Manually check the installed userscript on desktop Chrome and Firefox when possible. Never put ChatGPT credentials into automated tests.

- [ ] **New Chat:** wallpaper shows behind the greeting; Chat/Work switcher and compact rail stay legible.
- [ ] **Existing conversation:** wallpaper appears around transcript; no black dock/fade; text remains readable.
- [ ] **Work:** when available, the Work UI, controls, forms, overlays and dialogs remain functional.
- [ ] **Composer:** typing, sending, effort control, attachments and multiline expansion all work; the input retains an opaque background.
- [ ] **Navigation and viewport:** switch chats, resize near 1024 and 1676 pixels, toggle sidebar and refresh.
- [ ] **Theme:** disable Dreamscape to restore the native UI; re-enable to reveal the wallpaper.
- [ ] **Persistence:** switch, dim and reposition wallpapers; test custom upload and reload without losing preferences.
- [ ] **Accessibility/privacy:** Victor does not cover controls, reduced-motion behavior works, and reports contain no private chat content.

These manual checks **cannot be guaranteed** by fixture tests. For safe diagnostics and supported scope, see [Compatibility](COMPATIBILITY.md).

### Wallpaper readability and licensing

All five built-in wallpapers use light chat text over dark backgrounds. Because every display/browser renders contrast differently, manually verify each wallpaper with real ChatGPT messages and headings. Third-party photos and fan art are **not bundled** without distribution permission; users may import their own privately.
