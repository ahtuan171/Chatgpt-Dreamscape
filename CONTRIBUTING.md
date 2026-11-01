# Contributing

Thanks for helping improve Dreamscape!

1. Check existing issues before starting a change.
2. Keep desktop Chrome/Firefox compatibility in mind; don't expand scope to mobile without discussion.
3. Make focused changes in `src/`, rebuild `dist/` with `node tools/build.mjs`, and run `python tests/test_browser.py` before opening a PR.
4. Avoid global CSS selectors that might hide chat content. The conversation, composer, buttons, and sidebar must remain usable.
5. Never read, log, store, send or analyze ChatGPT conversation text. Keep custom wallpaper uploads local.
6. Don't add copyrighted images or sprites unless redistribution permission is documented in `ASSETS.md`.
7. Respect `prefers-reduced-motion` and keep animations unobtrusive.

Reports should include browser/version, desktop OS, screenshot (without private conversation content), reproduction steps and expected behavior. Please avoid uploading personal or sensitive chat logs.
