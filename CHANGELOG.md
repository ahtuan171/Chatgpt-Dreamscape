# Changelog / Lịch sử phiên bản

## v0.3.17 — 2026-11-21

- **Chat/Work update:** detect large opaque content-stage backdrops and reveal wallpapers while retaining the composer, navigation, controls and sidebar.
- **SPA transitions:** update and clear `.ds-stage` classes when the composer moves between page states.
- **Tests:** add screenshot-inspired 1024px/1676px layouts, toggle and navigation regressions. The build, syntax check and simulated Chromium suite passed on [PR #4](https://github.com/ahtuan171/Chatgpt-Dreamscape/pull/4).
- **Known limitation:** not validated in every real authenticated Chat/Work DOM. See [Compatibility](docs/COMPATIBILITY.md).

## v0.3.16 — 2026-11-05

- Handle deep `display: contents` conversation footer chains when clearing opaque docks.
- Regression for long-conversation footer ancestry. [PR #3](https://github.com/ahtuan171/Chatgpt-Dreamscape/pull/3).

## v0.3.15 — 2026-11-05

- Discover rounded composer surfaces without stable IDs; avoid styling full-width form backdrops.
- Add multiline and viewport regressions. [PR #2](https://github.com/ahtuan171/Chatgpt-Dreamscape/pull/2).

For installation, see the [README](README.md).
