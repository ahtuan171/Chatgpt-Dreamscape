  const customWallpapers=new Map();
  const customObjectUrls=new Map();
  const builtins=ASSETS.wallpapers;
  const findWallpaper=id=>builtins.find(w=>w.id===id)||customWallpapers.get(id);
  const allWallpapers=()=>[...builtins,...customWallpapers.values()];
  const activeWallpaper=()=>findWallpaper(settings.theme)||builtins[0];
  const clamp=(x,a,b)=>Math.min(b,Math.max(a,x));
  function wallpaperDim(id){const wall=findWallpaper(id);return clamp(Number(settings.dimOverrides[id]??wall?.dim??22)||0,0,75);}
  function wallpaperPosition(id){return clamp(Number(settings.positionOverrides[id]??50)||0,0,100);}
  function setWallpaperProperties(){
    const wallpaper=activeWallpaper();
    if(!findWallpaper(settings.theme)&&!String(settings.theme).startsWith('custom-'))settings.theme=wallpaper.id;
    const src=wallpaper.uri||customObjectUrls.get(wallpaper.id);
    if(src)document.documentElement.style.setProperty('--ds-wall',`url("${src}")`);
    document.documentElement.style.setProperty('--ds-dim',String(wallpaperDim(wallpaper.id)/100));
    // Built-in themes share a dark overlay, keeping conversation text readable.
    document.documentElement.classList.remove('ds-parchment');
    document.documentElement.style.setProperty('--ds-overlay-rgb','2,6,14');
    document.documentElement.style.setProperty('--ds-position',wallpaperPosition(wallpaper.id)+'%');
    document.documentElement.classList.toggle('ds-active',!!settings.enabled);
    if(victorElement)positionVictor();
    saveSettings();
  }
  async function loadCustomWallpapers(){
    try {
      const all=await listCustomWallpapers();
      for(const item of all){
        if(!item.blob)continue;
        customWallpapers.set(item.id,{id:item.id,name:item.name,dim:item.dim??20,custom:true});
        customObjectUrls.set(item.id,URL.createObjectURL(item.blob));
      }
    }catch(err){console.warn('[Dreamscape] Custom wallpapers unavailable:',err);showStatus('Custom wallpaper storage unavailable in this browser.');}
    // Unknown or removed built-in selections fall back to Moonlit Castle.
    // Do this after IndexedDB loads so saved custom choices are not reset.
    if(!findWallpaper(settings.theme))settings.theme=builtins[0].id;
    refreshThemePicker();setWallpaperProperties();
  }
  async function addWallpaper(file){
    const optimized=await optimizeWallpaper(file);
    const id='custom-'+(crypto.randomUUID?.()||String(Date.now())+'-'+Math.random().toString(36).slice(2));
    const name=(file.name||'My wallpaper').replace(/\.[^.]+$/,'').slice(0,62);
    await putCustomWallpaper({id,name,dim:20,blob:optimized});
    const url=URL.createObjectURL(optimized);
    customObjectUrls.set(id,url);
    customWallpapers.set(id,{id,name,dim:20,custom:true});
    settings.theme=id;saveSettings();refreshThemePicker();setWallpaperProperties();syncControls();
    showStatus(`Added “${name}” to My Wallpapers.`);
  }
  async function removeWallpaper(id){
    if(!customWallpapers.has(id))return;
    await deleteCustomWallpaper(id);
    customWallpapers.delete(id);
    URL.revokeObjectURL(customObjectUrls.get(id));
    customObjectUrls.delete(id);
    delete settings.dimOverrides[id];delete settings.positionOverrides[id];
    if(settings.theme===id)settings.theme=builtins[0].id;
    refreshThemePicker();setWallpaperProperties();syncControls();showStatus('Custom wallpaper deleted.');
  }
