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
    assert page.locator('.ds-theme option').count() == 5
    assert page.locator('.ds-panel').is_hidden()
    assert page.locator('html').evaluate("e=>e.classList.contains('ds-active')")
    assert page.locator('#ds-victor').evaluate('e=>getComputedStyle(e).display!="none"&&e.querySelector("canvas").getContext("2d").getImageData(0,0,148,118).data.some((v,i)=>i%4===3&&v>0)')
    victor_box=page.locator('#ds-victor').bounding_box()
    composer_box=page.locator('[data-testid="composer-root"]').bounding_box()
    assert victor_box['y'] < composer_box['y']
    effort_box=page.locator('.effort-control span').bounding_box()
    assert abs(victor_box['x']+victor_box['width']/2 - (effort_box['x']+effort_box['width']/2)) <= 4, (victor_box, effort_box)
    assert page.locator('#ds-victor').get_attribute('data-anchor') == 'effort' 
    assert page.locator('#ds-victor').count() == 1
    # Victor begins facing left and patrols toward the center from the upper-right corner.
    assert page.locator('#ds-victor').get_attribute('data-facing') == 'left'
    assert round(victor_box['width']) == 74 and round(victor_box['height']) == 59
    page.wait_for_timeout(6800)
    moved_box=page.locator('#ds-victor').bounding_box()
    assert moved_box['x'] < victor_box['x'] - 4, (moved_box,victor_box)
    assert moved_box['x'] >= composer_box['x'] + composer_box['width']*.5
    assert page.locator('#ds-victor').get_attribute('data-facing') == 'left'
    # Turn at the far edge, then walk back facing right, not moonwalk.
    page.wait_for_function("document.getElementById('ds-victor')?.dataset.facing==='right'",timeout=7000)
    assert page.locator('#ds-victor').get_attribute('data-facing') == 'right'
    page.wait_for_function("document.getElementById('ds-victor')?.dataset.motion==='walk' && document.getElementById('ds-victor')?.dataset.facing==='right'",timeout=5000)
    for sel in ['#thread-bottom', '#thread-bottom-container', '.outer-dock']:
        assert page.locator(sel).evaluate('e=>getComputedStyle(e).backgroundColor') == 'rgba(0, 0, 0, 0)', sel
    assert page.locator('[data-testid="composer-root"]').evaluate('e=>getComputedStyle(e).backgroundColor') == 'rgb(13, 18, 28)'
    assert page.locator('[data-testid="composer-root"]').evaluate('e=>getComputedStyle(e).backdropFilter') == 'none'
    assert page.locator('[data-testid="composer-root"]').evaluate('e=>getComputedStyle(e).color') == 'rgb(241, 243, 250)'
    assert not page.locator('.ds-status').is_visible()
    # Expanded composer / attachment-like UI must not revive a full-width black dock.
    page.locator('form').evaluate('e=>e.style.minHeight="240px"')
    page.locator('.outer-dock').evaluate('e=>e.style.height="300px"')
    page.wait_for_timeout(350)
    for selector in ['#thread-bottom','#thread-bottom-container','.outer-dock']:
        assert page.locator(selector).evaluate('e=>getComputedStyle(e).backgroundColor') == 'rgba(0, 0, 0, 0)', selector
    assert page.locator('#ds-victor').is_visible()
    folder = ROOT / 'tests/screenshots'
    folder.mkdir(exist_ok=True)
    page.screenshot(path=str(folder / 'expanded-composer.png'))
    page.locator('form').evaluate('e=>e.style.minHeight=""')
    page.locator('.outer-dock').evaluate('e=>e.style.height=""')
    page.wait_for_timeout(250)

    folder = ROOT / 'tests/screenshots'
    folder.mkdir(exist_ok=True)
    page.screenshot(path=str(folder / 'default.png'))
    page.locator('.ds-launch').click()
    assert page.locator('.ds-panel').is_visible()
    # Visible, keyboard-accessible checkmarks (not just text labels).
    controls = ['.ds-victor-check', '.ds-motion-check', '.ds-active-check']
    for selector in controls:
        input_box = page.locator(selector)
        assert input_box.is_visible(), selector
        assert input_box.is_checked(), selector
        rect = input_box.bounding_box()
        assert rect['width'] == 20 and rect['height'] == 20, (selector, rect)
        assert input_box.evaluate('e=>getComputedStyle(e, "::before").content') == '"✓"', selector
    assert len(controls)==3
    assert page.locator('.ds-glass-check').count() == 0
    assert not page.locator('html').evaluate("e=>e.classList.contains('ds-glass-composer')")
    assert page.locator('[data-testid="composer-root"]').evaluate('e=>getComputedStyle(e).backgroundColor') == 'rgb(13, 18, 28)'
    # Theme changes originate at one of four corners; the reveal covers the screen,
    # does not intercept input, and disappears after a smooth 720ms animation.
    old_wall=page.evaluate("document.documentElement.style.getPropertyValue('--ds-wall')")
    page.locator('.ds-theme').select_option('silent-king')
    page.wait_for_function("!!document.querySelector('.ds-wallpaper-reveal')")
    assert page.locator('.ds-wallpaper-reveal').evaluate("e=>getComputedStyle(e).pointerEvents==='none'")
    assert page.evaluate("document.documentElement.style.getPropertyValue('--ds-wall')") == old_wall
    anim=page.locator('.ds-wallpaper-reveal').evaluate("e=>e.getAnimations()[0].effect.getKeyframes().map(k=>k.clipPath)")
    assert anim[0].startswith('circle(0px at ') and anim[1].startswith('circle(150vmax at '),anim
    # Repeated selections must cancel the old effect and leave only one layer.
    page.locator('.ds-theme').select_option('arcane-library')
    assert page.locator('.ds-wallpaper-reveal').count()==1
    page.wait_for_timeout(800)
    assert page.locator('.ds-wallpaper-reveal').count()==0
    assert page.evaluate("document.documentElement.style.getPropertyValue('--ds-wall')") != old_wall
    assert page.locator('article h1').is_visible()
    page.emulate_media(reduced_motion='reduce')
    page.locator('.ds-theme').select_option('moonlit-castle')
    assert page.locator('.ds-wallpaper-reveal').count()==0
    page.emulate_media(reduced_motion='no-preference')
    assert page.locator('.ds-wall-preview').is_visible()
    assert page.locator('.ds-hint').inner_text().startswith('Changes wallpaper cropping')
    for theme in ['moonlit-castle', 'midnight-tulips', 'moonlit-romance', 'arcane-library', 'silent-king']:
        page.locator('.ds-theme').select_option(theme)
        page.wait_for_timeout(770)
        prop = page.evaluate("document.documentElement.style.getPropertyValue('--ds-wall')")
        assert prop.startswith('url("data:image/webp;base64,'), theme
        if theme in ('arcane-library', 'silent-king'):
            assert page.locator('.ds-wall-preview').evaluate('e=>getComputedStyle(e).backgroundImage.includes("data:image/webp;base64,")'), theme
            page.screenshot(path=str(folder / (theme + '.png')))
    page.locator('.ds-theme').select_option('moonlit-romance')
    page.wait_for_timeout(770)
    assert not page.locator('html').evaluate("e=>e.classList.contains('ds-parchment')")
    assert page.locator('.ds-overlay-label').inner_text() == 'Darken wallpaper'
    assert page.locator('article h1').evaluate('e=>getComputedStyle(e).color') != 'rgb(45, 33, 25)'
    page.screenshot(path=str(folder / 'moonlit-romance.png'))
    page.locator('.ds-theme').select_option('midnight-tulips')
    page.wait_for_timeout(770)
    page.locator('.ds-dim').fill('19')
    page.locator('.ds-dim').dispatch_event('input')
    assert page.locator('.ds-dim-value').inner_text() == '19%'
    page.locator('.ds-position').fill('30')
    page.locator('.ds-position').dispatch_event('input')
    assert page.evaluate("document.documentElement.style.getPropertyValue('--ds-position')") == '30%'
    page.screenshot(path=str(folder / 'tulips-menu.png'))
    page.locator('.ds-motion-check').uncheck()
    page.wait_for_timeout(200)
    assert page.locator('#ds-victor').get_attribute('data-motion') == 'idle'
    assert page.locator('#ds-victor').get_attribute('data-facing') == 'right'
    page.locator('.ds-motion-check').check()
    page.locator('.ds-victor-check').uncheck()
    assert page.locator('#ds-victor').is_hidden()
    page.locator('.ds-victor-check').check()
    assert page.locator('#ds-victor').is_visible()
    page.locator('.ds-active-check').uncheck()
    assert not page.locator('html').evaluate("e=>e.classList.contains('ds-active')")
    page.locator('.ds-active-check').check()
    page.locator('.ds-upload').set_input_files(str(ROOT / 'assets/wallpapers/midnight-tulips.webp'))
    page.wait_for_function("document.querySelector('.ds-theme')?.value.startsWith('custom-') && getComputedStyle(document.documentElement).getPropertyValue('--ds-wall').includes('blob:')")
    assert not errors, errors
    assert page.locator('.ds-theme option').count() == 6
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
        assert page.locator('.ds-theme option').count() == 6
        page.locator('.ds-launch').click()
    else:
        assert page.evaluate(f"window.__dreamscapeTestStores.records.has('{saved_id}')")
        assert saved_id in page.evaluate("window.__dreamscapeTestStores.settings.get('dreamscape-public-v1')")
    page.locator('.ds-delete').click()
    page.wait_for_timeout(200)
    assert page.locator('.ds-theme option').count() == 5
    assert page.locator('.ds-theme').input_value() == 'moonlit-castle'
    page.locator('form').evaluate('e=>e.removeAttribute("data-testid")')
    page.wait_for_timeout(400)
    assert page.locator('#ds-victor').is_visible()
    page.set_viewport_size({'width':1280,'height':720})
    page.wait_for_timeout(250)
    assert page.locator('article h1').is_visible()
    assert not errors, errors
    print(f"PASS ({'native IndexedDB' if real_storage else 'simulated storage'}): 5 themes, Victor over effort control with facing changes, visible persisted checkboxes, solid composer and dock styling, dim, position, upload, save, delete, fallback and resize")


def test_new_chat_composer(browser, use_mock_storage):
    """New Chat / SPA swaps: visible composer can be tall, non-form, or loaded later."""
    page = browser.new_page(viewport={'width':1600,'height':900})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content(FIXTURE)
    page.evaluate(STORAGE_SHIM)
    # Existing users may still have the retired option in localStorage.
    page.evaluate("localStorage.setItem('dreamscape-public-v1', JSON.stringify({glassComposer:true, victor:true}))")
    page.evaluate('''() => {
       // The old conversation composer can remain mounted while a new-chat
       // landing page presents a different, taller composer component.
       document.querySelector('#thread-bottom').style.display='none';
       const landing=document.createElement('section');
       landing.id='new-chat-landing';
       landing.style.cssText='position:fixed;inset:130px 200px 100px 300px;display:grid;place-items:center;';
       landing.innerHTML=`<div id="new-chat-composer" data-testid="composer-root" style="width:740px;height:390px;background:#252525;border-radius:22px;display:flex;align-items:flex-end;padding:24px;gap:18px">
         <div id="prompt-textarea-new" role="textbox" contenteditable="true" style="flex:1;min-height:35px">Ask ChatGPT</div>
         <button class="new-effort" type="button"><span>High</span></button>
         <button type="button">➤</button>
       </div>`;
       document.querySelector('#root').append(landing);
    }''')
    page.add_script_tag(content=SCRIPT)
    page.wait_for_timeout(550)
    assert page.locator('#ds-victor').is_visible(), 'Victor missing on fresh new-chat landing page'
    assert not page.evaluate("'glassComposer' in JSON.parse(localStorage.getItem('dreamscape-public-v1'))")
    assert page.locator('.ds-glass-check').count()==0
    assert page.locator('#ds-victor').get_attribute('data-anchor')=='effort'
    cat=page.locator('#ds-victor').bounding_box()
    target=page.locator('.new-effort span').bounding_box()
    assert abs(cat['x']+cat['width']/2-target['x']-target['width']/2)<5
    page.locator('#ds-victor').click()
    assert page.locator('#ds-victor').get_attribute('data-reaction')=='petted'
    # Route to a conversation: old dock becomes visible, new-chat UI removed.
    page.evaluate('''() => {
      document.querySelector('#new-chat-landing').remove();
      document.querySelector('#thread-bottom').style.display='flex';
    }''')
    page.wait_for_timeout(400)
    assert page.locator('#ds-victor').is_visible()
    assert page.locator('#ds-victor').get_attribute('data-anchor')=='effort'
    # Go back to new chat; no form or testid, just an editable and toolbar.
    page.evaluate('''() => {
      document.querySelector('#thread-bottom').style.display='none';
      const region=document.createElement('div');
      region.id='new-chat-landing';
      region.style.cssText='position:fixed;top:370px;left:450px;width:740px;height:160px;display:flex;align-items:center;background:#1d1d1d;border-radius:16px;';
      region.innerHTML=`<div id="prompt-textarea" role="textbox" contenteditable="true" style="flex:1">Ask anything</div><button class="new-effort"><span>Medium</span></button>`;
      document.querySelector('#root').append(region);
    }''')
    page.wait_for_timeout(400)
    assert page.locator('#ds-victor').is_visible(), 'Victor missing on form-free new-chat layout'
    assert page.locator('#ds-victor').get_attribute('data-anchor')=='effort'
    # Temporary style-only hide/reveal (SPA or animation), without childList mutations.
    page.locator('#new-chat-landing').evaluate("e=>e.style.display='none'")
    page.wait_for_timeout(300)
    assert page.locator('#ds-victor').is_hidden(), 'Victor must hide when no usable composer is visible'
    page.locator('#new-chat-landing').evaluate("e=>e.style.display='flex'")
    page.wait_for_timeout(450)
    assert page.locator('#ds-victor').is_visible(), 'Victor not restored by CSS-only layout change'
    assert not errors, errors
    page.screenshot(path=str(ROOT/'tests/screenshots/new-chat-victor.png'))
    page.close()
    print('PASS: Victor works on new-chat landing (tall component, form-free composer, SPA swaps, CSS-only reveal)')

def test_victor_interaction(browser, url, use_mock_storage):
    """Victor should perch over the effort control and respond to clicks and keyboard."""
    page = browser.new_page(viewport={'width':1600,'height':900}, reduced_motion='no-preference')
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    if use_mock_storage:
        page.set_content(FIXTURE)
        page.evaluate(STORAGE_SHIM)
    else:
        page.goto(url)
    page.add_script_tag(content=SCRIPT)
    page.wait_for_function("() => document.querySelector('#ds-victor')?.dataset.anchor==='effort'")
    rect=page.locator('#ds-victor').bounding_box()
    effort=page.locator('.effort-control span').bounding_box()
    composer=page.locator('form').bounding_box()
    assert abs(rect['x']+rect['width']/2-effort['x']-effort['width']/2)<5, (rect,effort)
    assert rect['y']+rect['height'] <= composer['y']+12
    assert page.locator('#ds-victor').evaluate('e=>e.tagName')=='BUTTON'
    assert page.locator('#ds-victor').get_attribute('aria-label')=='Pet Victor the pixel cat'
    assert page.locator('#ds-victor').evaluate('e=>getComputedStyle(e).pointerEvents')=='auto'

    # The hitbox itself is clickable, not just a decorative overlay.
    page.locator('#ds-victor').click()
    assert page.locator('#ds-victor').get_attribute('data-reaction')=='petted'
    page.wait_for_timeout(250)
    assert page.locator('.ds-victor-heart').evaluate('e=>getComputedStyle(e).opacity')!='0'
    assert page.locator('#ds-victor canvas').evaluate('e=>getComputedStyle(e).animationName')=='ds-victor-hop'
    folder=ROOT/'tests/screenshots'
    folder.mkdir(exist_ok=True)
    page.screenshot(path=str(folder/'victor-click.png'))
    page.wait_for_function("() => document.querySelector('#ds-victor')?.dataset.reaction==='idle'")
    # Keyboard users should get the same response (native button behavior).
    page.locator('#ds-victor').focus()
    page.keyboard.press('Enter')
    assert page.locator('#ds-victor').get_attribute('data-reaction')=='petted'
    page.wait_for_timeout(900)

    # Effort selector can shift as the composer grows (attachments, multiline input).
    page.locator('form').evaluate('e=>e.style.minHeight="228px"')
    page.locator('.effort-control').evaluate('e=>e.style.transform="translateX(-35px)"')
    page.wait_for_timeout(300)
    grown_cat=page.locator('#ds-victor').bounding_box()
    grown_label=page.locator('.effort-control span').bounding_box()
    grown_composer=page.locator('form').bounding_box()
    assert abs(grown_cat['x']+grown_cat['width']/2-grown_label['x']-grown_label['width']/2)<5
    assert grown_cat['y']+grown_cat['height']<=grown_composer['y']+12

    # If effort changes, Victor tracks its location without modifying composer controls.
    page.locator('.effort-control span').evaluate("e=>e.textContent='Medium'")
    page.wait_for_timeout(250)
    assert page.locator('#ds-victor').get_attribute('data-anchor')=='effort'
    page.locator('.effort-control').evaluate("e=>e.remove()")
    page.wait_for_timeout(250)
    assert page.locator('#ds-victor').get_attribute('data-anchor')=='fallback'
    assert page.locator('#ds-victor').is_visible()
    page.locator('#prompt-textarea').click()
    page.keyboard.type('Hello Victor')
    assert 'Hello Victor' in page.locator('#prompt-textarea').inner_text()
    assert not errors,errors
    page.close()

    # Respect OS reduced-motion setting; petting should still acknowledge a click.
    page=browser.new_page(viewport={'width':1600,'height':900}, reduced_motion='reduce')
    if use_mock_storage:
        page.set_content(FIXTURE)
        page.evaluate(STORAGE_SHIM)
    else:
        page.goto(url)
    page.add_script_tag(content=SCRIPT)
    page.wait_for_function("() => document.querySelector('#ds-victor')?.dataset.anchor==='effort'")
    page.locator('#ds-victor').click()
    assert page.locator('#ds-victor').get_attribute('data-reaction')=='petted'
    assert page.locator('#ds-victor canvas').evaluate('e=>getComputedStyle(e).animationName')=='none'
    assert page.locator('.ds-victor-heart').evaluate('e=>getComputedStyle(e).opacity')=='1'
    page.close()
    print('PASS: Victor sits above High, follows effort label, falls back safely, click/keyboard pet with reduced-motion support')

def test_existing_selection_migration(browser, url, use_mock_storage):
    """Retired themes fall back, while saved custom wallpapers remain selected."""
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    if use_mock_storage:
        page.set_content(FIXTURE)
        page.evaluate(STORAGE_SHIM)
    else:
        page.goto(url)
    page.evaluate("""() => localStorage.setItem('dreamscape-public-v1',
        JSON.stringify({enabled:true, theme:'vintage-letter', victor:true,
                        motion:true, dimOverrides:{}, positionOverrides:{}}))""")
    page.add_script_tag(content=SCRIPT)
    page.wait_for_function("() => document.querySelector('.ds-theme')?.value === 'moonlit-castle'")
    assert page.locator('.ds-theme option').count() == 5
    assert page.evaluate("JSON.parse(localStorage.getItem('dreamscape-public-v1')).theme") == 'moonlit-castle'
    assert not page.locator('html').evaluate("e=>e.classList.contains('ds-parchment')")
    page.close()

    # Existing personal wallpaper is not inadvertently replaced by the fallback.
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    if use_mock_storage:
        page.set_content(FIXTURE)
        page.evaluate(STORAGE_SHIM)
    else:
        page.goto(url)
    page.evaluate("""() => {
      const id='custom-kept-by-upgrade';
      localStorage.setItem('dreamscape-public-v1',JSON.stringify({
        enabled:true, theme:id, victor:true, motion:true,
        dimOverrides:{}, positionOverrides:{}}));
    }""")
    if use_mock_storage:
        page.evaluate("""() => window.__dreamscapeTestStores.records.set(
          'custom-kept-by-upgrade',
          {id:'custom-kept-by-upgrade',name:'Kept wallpaper',dim:20,
           blob:new Blob(['data'],{type:'image/webp'})})""")
    else:
        page.evaluate("""() => new Promise((resolve,reject)=>{
          const req=indexedDB.open('dreamscape-wallpapers-v1',1);
          req.onupgradeneeded=()=>req.result.createObjectStore('wallpapers',{keyPath:'id'});
          req.onerror=()=>reject(req.error);
          req.onsuccess=()=>{
            const db=req.result;
            const tx=db.transaction('wallpapers','readwrite');
            tx.objectStore('wallpapers').put({id:'custom-kept-by-upgrade',name:'Kept wallpaper',dim:20,
              blob:new Blob(['data'],{type:'image/webp'})});
            tx.oncomplete=()=>{db.close();resolve()};
            tx.onerror=()=>reject(tx.error);
          };
        })""")
    page.add_script_tag(content=SCRIPT)
    page.wait_for_function("() => document.querySelector('.ds-theme')?.value === 'custom-kept-by-upgrade'")
    assert page.locator('.ds-theme option').count() == 6
    assert page.evaluate("JSON.parse(localStorage.getItem('dreamscape-public-v1')).theme") == 'custom-kept-by-upgrade'
    page.close()
    print('PASS: retired Vintage Letter migrates to Moonlit Castle; existing personal wallpaper preserved')

def test_attachment_dock_reparent(browser, url, use_mock_storage):
    """Regression: same composer element, new opaque dock wrappers and a backdrop sibling."""
    from io import BytesIO
    from PIL import Image
    page = browser.new_page(viewport={'width':1600,'height':900})
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    if use_mock_storage:
        page.set_content(FIXTURE)
        page.evaluate(STORAGE_SHIM)
    else:
        page.goto(url)
    page.add_script_tag(content=SCRIPT)
    page.wait_for_function("() => !!document.querySelector('#dreamscape-app')")
    page.wait_for_timeout(350)
    # Pixel outside the composer and inside the opaque strip introduced below.
    original = Image.open(BytesIO(page.screenshot())).convert('RGB').getpixel((310, 710))
    page.evaluate('''() => {
      const form=document.querySelector('form[data-testid="composer-root"]');
      const dock=document.createElement('div');
      dock.className='new-black-dock';
      dock.style.cssText='position:fixed;left:14px;right:14px;bottom:0;height:275px;background:#000;display:flex;align-items:center;justify-content:center;z-index:50;';
      const overlay=document.createElement('div');
      overlay.className='decorative-dock-background';
      // No aria-hidden or pointer-events hint: ordinary decorative divs.
      overlay.style.cssText='position:absolute;inset:0;background:#000;z-index:0;';
      overlay.innerHTML='<div class="nested-backdrop" style="position:absolute;inset:0;background:linear-gradient(#000,#000)"></div>';
      const style=document.createElement('style');
      style.textContent='.nested-backdrop::before{content:"";position:absolute;inset:0;background:#000;backdrop-filter:blur(8px)}';
      document.head.append(style);
      const controls=document.createElement('div');
      controls.className='dock-controls';
      controls.style.cssText='position:absolute;left:0;bottom:0;background:rgb(20,30,40);z-index:2';
      controls.innerHTML='<button type="button">Keep controls</button>';
      controls.onclick=()=>controls.dataset.clicked='yes';
      dock.append(controls);
      dock.appendChild(overlay);
      // Actual ChatGPT footer chain contains boxless React layout wrappers.
      // Backdrops with pointer-events:none are absent from elementsFromPoint.
      overlay.style.pointerEvents='none';
      const contents=document.createElement('div');
      contents.style.display='contents';
      dock.append(contents);
      let node=contents;
      for(let i=0;i<12;i++){
        const inner=document.createElement('div');
        inner.className='nested-dark n'+i;
        inner.style.cssText='position:relative;background:#000;width:100%;height:100%;display:flex;align-items:center;justify-content:center;';
        node.appendChild(inner);node=inner;
      }
      form.style.cssText='min-height:245px;z-index:1;';
      node.appendChild(form);
      document.querySelector('.outer-dock').remove();
      document.querySelector('#root').appendChild(dock);
    }''')
    page.wait_for_timeout(450)
    assert page.locator('form[data-testid="composer-root"]').count() == 1
    for selector in ['.new-black-dock', '.nested-dark', '.decorative-dock-background', '.nested-backdrop']:
        colors=page.locator(selector).evaluate_all('es=>es.map(e=>getComputedStyle(e).backgroundColor)')
        assert all(x=='rgba(0, 0, 0, 0)' for x in colors), (selector, colors)
    assert page.locator('.nested-backdrop').evaluate('e=>getComputedStyle(e,"::before").backgroundColor') == 'rgba(0, 0, 0, 0)'
    assert page.locator('.nested-backdrop').evaluate('e=>getComputedStyle(e,"::before").backdropFilter') == 'none'
    assert page.locator('.dock-controls').evaluate('e=>getComputedStyle(e).backgroundColor') == 'rgb(20, 30, 40)'
    page.locator('.dock-controls button').click()
    assert page.locator('.dock-controls').get_attribute('data-clicked') == 'yes'
    assert page.locator('.nested-dark').count() == 12
    assert page.locator('article').evaluate('e=>!e.classList.contains("ds-dock")')
    assert page.locator('article h1').is_visible()
    assert page.locator('#ds-victor').is_visible()
    assert page.locator('form').evaluate('e=>getComputedStyle(e).backgroundColor')=='rgb(13, 18, 28)'
    output=ROOT/'tests/screenshots/attachment-dock-regression.png'
    page.screenshot(path=str(output))
    after=Image.open(output).convert('RGB').getpixel((310,710))
    assert max(abs(a-b) for a,b in zip(original,after))<=3, (original,after)
    # Same form expands again; no new composer element is created.
    page.locator('form').evaluate('e=>e.style.minHeight="275px"')
    page.locator('.new-black-dock').evaluate('e=>e.style.height="325px"')
    page.wait_for_timeout(350)
    assert page.locator('.decorative-dock-background').evaluate('e=>getComputedStyle(e).backgroundColor')=='rgba(0, 0, 0, 0)'
    page.locator('.ds-launch').click()
    page.locator('.ds-active-check').uncheck()
    assert page.locator('.decorative-dock-background').evaluate('e=>getComputedStyle(e).backgroundColor') == 'rgb(0, 0, 0)'
    page.locator('.ds-active-check').check()
    assert page.locator('.nested-backdrop').evaluate('e=>getComputedStyle(e).backgroundImage') == 'none'
    assert not errors, errors
    print('PASS: reparented and expanded composer; 12 opaque ancestors and black decorative sibling transparent (pixel + DOM checks)')
    page.close()


def test_nested_composer_surface(browser, url, use_mock_storage):
    """Full-width form wraps a separate painted input and in-flow backdrop."""
    page = browser.new_page(viewport={'width':1600,'height':900})
    if use_mock_storage:
        page.set_content(FIXTURE)
        page.evaluate(STORAGE_SHIM)
    else:
        page.goto(url)
    page.evaluate('''() => {
      const form=document.querySelector('form');
      document.querySelector('#thread-bottom').style.minHeight='275px';
      document.querySelector('#thread-bottom-container').style.minHeight='275px';
      document.querySelector('.outer-dock').style.height='275px';
      const surface=document.createElement('div');
      surface.id='composer-background';
      surface.setAttribute('data-composer-surface','true');
      surface.style.cssText='width:750px;min-height:245px;background:#1c1c1c;border-radius:21px;padding:22px;position:relative;z-index:1;display:flex;align-items:flex-end';
      while(form.firstChild)surface.append(form.firstChild);
      form.removeAttribute('data-testid');
      form.style.cssText='width:100%;min-height:275px;background:#000;display:flex;justify-content:center;position:relative;padding:0;border:0;border-radius:0';
      form.append(surface);
      const layer=document.createElement('div');
      layer.className='in-flow-backdrop';
      layer.style.cssText='position:relative;width:100%;height:275px;margin-left:-100%;background:#000;pointer-events:none';
      layer.innerHTML='<div style="width:100%;height:100%;background:linear-gradient(#000,#000)"></div>';
      form.append(layer);
    }''')
    page.add_script_tag(content=SCRIPT)
    page.wait_for_function("document.querySelector('[data-composer-surface]').classList.contains('ds-composer')")
    assert page.locator('form').evaluate("e=>getComputedStyle(e).backgroundColor") == 'rgba(0, 0, 0, 0)'
    assert page.locator('[data-composer-surface]').evaluate("e=>getComputedStyle(e).backgroundColor") == 'rgb(13, 18, 28)'
    assert page.locator('.in-flow-backdrop').evaluate("e=>getComputedStyle(e).backgroundColor") == 'rgba(0, 0, 0, 0)'
    assert page.locator('.in-flow-backdrop > div').evaluate("e=>getComputedStyle(e).backgroundImage") == 'none'
    assert page.locator('article h1').is_visible()
    page.locator('#prompt-textarea').fill('Composer remains editable')
    assert page.locator('#prompt-textarea').inner_text() == 'Composer remains editable'
    page.locator('[data-composer-surface] button').last.click()
    page.screenshot(path=str(ROOT/'tests/screenshots/nested-composer-surface.png'))
    page.close()
    print('PASS: full-width form transparent; nested painted input, in-flow backdrop, editor and controls preserved')


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
        test_new_chat_composer(browser, not real_storage)
        test_victor_interaction(browser, url, not real_storage)
        run_tests(page, real_storage)
        test_existing_selection_migration(browser, url, not real_storage)
        test_attachment_dock_reparent(browser, url, not real_storage)
        test_nested_composer_surface(browser, url, not real_storage)
        browser.close()
    server.shutdown()
