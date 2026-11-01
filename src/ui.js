  let interfaceRoot=null;
  function showStatus(message){
    if(!interfaceRoot)return;
    const status=interfaceRoot.querySelector('.ds-status');
    status.textContent=message;
    status.hidden=false;
  }
  function refreshThemePicker(){
    if(!interfaceRoot)return;
    const select=interfaceRoot.querySelector('.ds-theme');
    select.replaceChildren();
    const groups=new Map();
    for(const wall of builtins){
      const label=wall.group||'Dreamscape Originals';
      if(!groups.has(label)){
        const optgroup=document.createElement('optgroup');optgroup.label=label;
        groups.set(label,optgroup);select.append(optgroup);
      }
      groups.get(label).append(new Option(wall.name,wall.id));
    }
    if(customWallpapers.size){
      const custom=document.createElement('optgroup');custom.label='My Wallpapers';
      for(const wall of customWallpapers.values())custom.append(new Option(wall.name,wall.id));
      select.append(custom);
    }
    select.value=settings.theme;
  }
  function syncControls(){
    if(!interfaceRoot)return;
    const wallpaper=activeWallpaper();
    interfaceRoot.querySelector('.ds-theme').value=wallpaper.id;
    interfaceRoot.querySelector('.ds-dim').value=wallpaperDim(wallpaper.id);
    interfaceRoot.querySelector('.ds-dim-value').textContent=wallpaperDim(wallpaper.id)+'%';
    interfaceRoot.querySelector('.ds-overlay-label').textContent='Darken wallpaper';
    interfaceRoot.querySelector('.ds-position').value=wallpaperPosition(wallpaper.id);
    interfaceRoot.querySelector('.ds-position-value').textContent=wallpaperPosition(wallpaper.id)+'%';
    interfaceRoot.querySelector('.ds-victor-check').checked=!!settings.victor;
    interfaceRoot.querySelector('.ds-motion-check').checked=!!settings.motion;
    interfaceRoot.querySelector('.ds-active-check').checked=!!settings.enabled;
    interfaceRoot.querySelector('.ds-glass-check').checked=!!settings.glassComposer;
    interfaceRoot.querySelector('.ds-delete').hidden=!wallpaper.custom;
    const preview=interfaceRoot.querySelector('.ds-wall-preview');
    if(preview){
      const src=wallpaper.uri||customObjectUrls.get(wallpaper.id);
      preview.style.backgroundImage=src?`linear-gradient(rgba(2,6,14,.16),rgba(2,6,14,.16)),url("${src}")`:'none';
      preview.setAttribute('aria-label',wallpaper.name+' preview');
    }
  }
  function installUI(){
    interfaceRoot=document.createElement('div');interfaceRoot.id='dreamscape-app';
    interfaceRoot.innerHTML=`
      <button class="ds-launch" type="button" aria-label="Open Dreamscape settings" aria-expanded="false" aria-controls="ds-settings" title="Dreamscape settings">☾</button>
      <section class="ds-panel" id="ds-settings" role="region" aria-label="Dreamscape settings" hidden>
        <div class="ds-heading"><strong>☾ Dreamscape</strong><button class="ds-close" type="button" aria-label="Close settings">×</button></div>
        <label for="ds-theme">Wallpaper</label>
        <select class="ds-theme" id="ds-theme"></select>
        <div class="ds-wall-preview" role="img" aria-label="Selected wallpaper preview"></div>
        <label for="ds-dim"><span class="ds-overlay-label">Darken wallpaper</span> <output class="ds-dim-value"></output></label>
        <input class="ds-dim" id="ds-dim" type="range" min="0" max="75" step="1">
        <label for="ds-position">Horizontal position <output class="ds-position-value"></output></label>
        <input class="ds-position" id="ds-position" type="range" min="0" max="100" step="5">
        <span class="ds-hint">Changes wallpaper cropping: 0% left · 50% center · 100% right.</span>
        <div class="ds-actions">
          <label class="ds-upload-label" for="ds-upload">＋ Add wallpaper</label>
          <input class="ds-upload" id="ds-upload" type="file" accept="image/png,image/jpeg,image/webp" hidden>
          <button class="ds-delete" type="button" hidden>Delete selected</button>
        </div>
        <div class="ds-separator"></div>
        <label class="ds-choice"><input class="ds-victor-check" type="checkbox"> Victor · pixel companion</label>
        <label class="ds-choice"><input class="ds-motion-check" type="checkbox"> Gentle animations</label>
        <label class="ds-choice"><input class="ds-glass-check" type="checkbox"> Translucent composer (show wallpaper)</label>
        <label class="ds-choice"><input class="ds-active-check" type="checkbox"> Enable Dreamscape</label>
        <div class="ds-status" role="status" hidden></div>
        <small>Your wallpapers and settings stay in this browser. Nothing is uploaded.</small>
      </section>`;
    document.body.append(interfaceRoot);
    const get=s=>interfaceRoot.querySelector(s);
    const launch=get('.ds-launch');const panel=get('.ds-panel');
    const toggle=open=>{
      panel.hidden=!open;launch.setAttribute('aria-expanded',String(open));
      if(open)syncControls();
    };
    launch.addEventListener('click',()=>toggle(panel.hidden));
    get('.ds-close').addEventListener('click',()=>toggle(false));
    document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!panel.hidden)toggle(false);});
    get('.ds-theme').addEventListener('change',e=>{settings.theme=e.target.value;setWallpaperProperties();syncControls();});
    get('.ds-dim').addEventListener('input',e=>{settings.dimOverrides[settings.theme]=Number(e.target.value);setWallpaperProperties();syncControls();});
    get('.ds-position').addEventListener('input',e=>{settings.positionOverrides[settings.theme]=Number(e.target.value);setWallpaperProperties();syncControls();});
    for(const [selector,key] of [['.ds-victor-check','victor'],['.ds-motion-check','motion'],['.ds-glass-check','glassComposer'],['.ds-active-check','enabled']]){
      get(selector).addEventListener('change',e=>{settings[key]=e.target.checked;setWallpaperProperties();saveSettings();drawVictor();});
    }
    get('.ds-upload').addEventListener('change',async e=>{
      const file=e.target.files?.[0];if(!file)return;
      try{await addWallpaper(file);}catch(err){showStatus(err?.message||'Could not add wallpaper.');}
      e.target.value='';
    });
    get('.ds-delete').addEventListener('click',async()=>{
      if(!customWallpapers.has(settings.theme))return;
      try{await removeWallpaper(settings.theme);}catch(err){showStatus(err?.message||'Unable to delete wallpaper.');}
    });
    refreshThemePicker();syncControls();
  }
