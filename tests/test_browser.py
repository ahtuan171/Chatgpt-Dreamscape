"""Browser smoke tests. Uses real loopback origin when permitted; restricted environments use mocked storage."""
import http.server
import socketserver
import threading
from pathlib import Path
from playwright.sync_api import Error, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (ROOT / 'dist/dreamscape.user.js').read_text()
FIXTURE = (ROOT / 'tests/chatgpt-fixture.html').read_text()

# about:blank browser origins forbid storage in some sandboxes. These minimal shims
# cover the same async UI code paths, without claiming native IndexedDB coverage.
STORAGE_SHIM = r"""
(() => {
  const settings = new Map();
  const records = new Map();
  Object.defineProperty(window, 'localStorage', { configurable: true, value: {
    getItem: k => settings.has(k) ? settings.get(k) : null,
    setItem: (k,v) => settings.set(k, String(v)),
    removeItem: k => settings.delete(k)
  }});
  const request = result => {
    const req = {result};
    queueMicrotask(() => req.onsuccess?.({target:req}));
    return req;
  };
  const db = {
    objectStoreNames: {contains: () => true},
    createObjectStore: () => {},
    close: () => {},
    transaction: () => ({
      objectStore: () => ({
        getAll: () => request(Array.from(records.values())),
        put: item => { records.set(item.id, item); return request(item.id); },
        delete: id => { records.delete(id); return request(undefined); }
      })
    })
  };
  Object.defineProperty(window, 'indexedDB', {configurable: true, value:{open:()=>request(db)}});
  window.__dreamscapeTestStores = {settings, records};
})();
"""

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)
    def log_message(self, *args):
        pass

class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


def run_tests(page, real_storage):
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.add_script_tag(content=SCRIPT)
    page.wait_for_timeout(700)
    assert not errors, errors
    assert page.locator('#dreamscape-app').count() == 1
    assert page.locator('article h1').is_visible()
    assert page.locator('#sidebar').is_visible()
    assert page.locator('.ds-theme option').count() == 10
    assert page.locator('.ds-panel').is_hidden()
    assert page.locator('html').evaluate("e=>e.classList.contains('ds-active')")
    assert page.locator('#ds-victor').evaluate('e=>getComputedStyle(e).display!="none"&&e.querySelector("canvas").getContext("2d").getImageData(0,0,116,92).data.some((v,i)=>i%4===3&&v>0)')
    victor_box=page.locator('#ds-victor').bounding_box()
    composer_box=page.locator('[data-testid="composer-root"]').bounding_box()
    assert victor_box['y'] < composer_box['y']
    assert composer_box['x'] <= victor_box['x'] <= composer_box['x']+composer_box['width']*.19
    assert page.locator('#ds-victor').count() == 1
    # Natural short patrol should move Victor only within the left part of composer.
    page.wait_for_timeout(6800)
    moved_box=page.locator('#ds-victor').bounding_box()
    assert moved_box['x'] > victor_box['x'] + 4, (moved_box,victor_box)
    assert moved_box['x'] <= composer_box['x'] + composer_box['width']*.30
    for sel in ['#thread-bottom', '#thread-bottom-container', '.outer-dock']:
        assert page.locator(sel).evaluate('e=>getComputedStyle(e).backgroundColor') == 'rgba(0, 0, 0, 0)', sel
    assert page.locator('[data-testid="composer-root"]').evaluate('e=>getComputedStyle(e).backgroundColor') == 'rgb(13, 18, 28)'
    assert not page.locator('.ds-status').is_visible()

    folder = ROOT / 'tests/screenshots'
    folder.mkdir(exist_ok=True)
    page.screenshot(path=str(folder / 'default.png'))
    page.locator('.ds-launch').click()
    assert page.locator('.ds-panel').is_visible()
    assert page.locator('.ds-wall-preview').is_visible()
    assert page.locator('.ds-hint').inner_text().startswith('Changes wallpaper cropping')
    for theme in ['moonlit-castle', 'midnight-tulips', 'luminous-garden', 'starlit-forest', 'violet-city', 'golden-wildflowers', 'quiet-library', 'chess-at-night', 'piano-nocturne', 'moonlit-village']:
        page.locator('.ds-theme').select_option(theme)
        prop = page.evaluate("document.documentElement.style.getPropertyValue('--ds-wall')")
        assert prop.startswith('url("data:image/webp;base64,'), theme
    page.locator('.ds-theme').select_option('midnight-tulips')
    page.locator('.ds-dim').fill('19')
    page.locator('.ds-dim').dispatch_event('input')
    assert page.locator('.ds-dim-value').inner_text() == '19%'
    page.locator('.ds-position').fill('30')
    page.locator('.ds-position').dispatch_event('input')
    assert page.evaluate("document.documentElement.style.getPropertyValue('--ds-position')") == '30%'
    page.screenshot(path=str(folder / 'tulips-menu.png'))
    page.locator('.ds-victor-check').uncheck()
    assert page.locator('#ds-victor').is_hidden()
    page.locator('.ds-victor-check').check()
    assert page.locator('#ds-victor').is_visible()
    page.locator('.ds-active-check').uncheck()
    assert not page.locator('html').evaluate("e=>e.classList.contains('ds-active')")
    page.locator('.ds-active-check').check()
    page.locator('.ds-upload').set_input_files(str(ROOT / 'assets/wallpapers/midnight-tulips.webp'))
    page.wait_for_timeout(800)
    assert not errors, errors
    assert page.locator('.ds-theme option').count() == 11
    saved_id = page.locator('.ds-theme').input_value()
    assert saved_id.startswith('custom-'), saved_id
    assert page.locator('.ds-delete').is_visible()
    assert page.locator('.ds-status').inner_text().startswith('Added')
    assert page.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--ds-wall').includes('blob:')")

    if real_storage:
        # Only the HTTP-origin test checks native IndexedDB persistence across reload.
        page.reload()
        page.add_script_tag(content=SCRIPT)
        page.wait_for_timeout(650)
        assert page.locator('.ds-theme').input_value() == saved_id
        assert page.locator('.ds-theme option').count() == 11
        page.locator('.ds-launch').click()
    else:
        assert page.evaluate(f"window.__dreamscapeTestStores.records.has('{saved_id}')")
        assert saved_id in page.evaluate("window.__dreamscapeTestStores.settings.get('dreamscape-public-v1')")
    page.locator('.ds-delete').click()
    page.wait_for_timeout(200)
    assert page.locator('.ds-theme option').count() == 10
    assert page.locator('.ds-theme').input_value() == 'moonlit-village'
    page.locator('form').evaluate('e=>e.removeAttribute("data-testid")')
    page.wait_for_timeout(400)
    assert page.locator('#ds-victor').is_visible()
    page.set_viewport_size({'width':1280,'height':720})
    page.wait_for_timeout(250)
    assert page.locator('article h1').is_visible()
    assert not errors, errors
    print(f"PASS ({'native IndexedDB' if real_storage else 'simulated storage'}): 10 themes, Victor single-canvas display, composer dock, dim, position, upload, save, delete, fallback and resize")

with Server(('127.0.0.1', 0), Handler) as server:
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{server.server_address[1]}/tests/chatgpt-fixture.html'
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None,
                                    headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        page = browser.new_page(viewport={'width':1600,'height':900}, accept_downloads=True)
        real_storage = True
        try:
            page.goto(url, timeout=9000)
        except Error as e:
            if 'ERR_BLOCKED_BY_ADMINISTRATOR' not in str(e):
                raise
            real_storage = False
            page.set_content(FIXTURE)
            page.evaluate(STORAGE_SHIM)
            print('NOTE: browser navigation restricted; using about:blank fixture with simulated storage. Native IndexedDB must be tested in CI.')
        run_tests(page, real_storage)
        browser.close()
    server.shutdown()
