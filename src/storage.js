  // Local-only preferences and wallpaper storage. No external APIs.
  const STORAGE_KEY = 'dreamscape-public-v1';
  const STORE_DB = 'dreamscape-wallpapers-v1';
  const STORE = 'wallpapers';
  const DEFAULTS = {enabled:true, theme:'moonlit-castle', victor:true, motion:true, glassComposer:true, dimOverrides:{}, positionOverrides:{}};
  let userSettings = {};
  try { userSettings = JSON.parse(localStorage.getItem(STORAGE_KEY)||'{}') || {}; } catch {}
  const settings = {...DEFAULTS, ...userSettings};
  settings.dimOverrides = settings.dimOverrides && typeof settings.dimOverrides === 'object' ? settings.dimOverrides : {};
  settings.positionOverrides = settings.positionOverrides && typeof settings.positionOverrides === 'object' ? settings.positionOverrides : {};
  function saveSettings() {
    try {localStorage.setItem(STORAGE_KEY,JSON.stringify(settings));}catch(err){console.warn('[Dreamscape] Could not save preferences',err);}
  }
  function openWallDB(){
    return new Promise((resolve,reject)=>{
      const request=indexedDB.open(STORE_DB,1);
      request.onupgradeneeded=()=>{if(!request.result.objectStoreNames.contains(STORE))request.result.createObjectStore(STORE,{keyPath:'id'});};
      request.onsuccess=()=>resolve(request.result);
      request.onerror=()=>reject(request.error);
    });
  }
  async function dbOperation(mode,callback){
    const db=await openWallDB();
    try {return await new Promise((resolve,reject)=>{
      const tx=db.transaction(STORE,mode);
      const request=callback(tx.objectStore(STORE));
      request.onsuccess=()=>resolve(request.result);
      request.onerror=()=>reject(request.error);
      tx.onabort=()=>reject(tx.error||new Error('Wallpaper storage transaction aborted'));
    });} finally {db.close();}
  }
  const listCustomWallpapers=()=>dbOperation('readonly',store=>store.getAll());
  const putCustomWallpaper=wallpaper=>dbOperation('readwrite',store=>store.put(wallpaper));
  const deleteCustomWallpaper=id=>dbOperation('readwrite',store=>store.delete(id));

  async function optimizeWallpaper(file){
    if (!['image/png','image/jpeg','image/webp'].includes(file.type)) throw new Error('Use a PNG, JPG or WebP image.');
    if (file.size>15*1024*1024)throw new Error('Choose an image smaller than 15 MB.');
    const localURL=URL.createObjectURL(file);
    let bitmap;
    try {
      const img=new Image();
      img.src=localURL;
      await img.decode();
      if (!img.naturalWidth || !img.naturalHeight) throw new Error('Cannot open this image.');
      const ratio=Math.min(1,2400/img.naturalWidth,1600/img.naturalHeight);
      const canvas=document.createElement('canvas');
      canvas.width=Math.max(1,Math.round(img.naturalWidth*ratio));
      canvas.height=Math.max(1,Math.round(img.naturalHeight*ratio));
      canvas.getContext('2d').drawImage(img,0,0,canvas.width,canvas.height);
      const blob=await new Promise(resolve=>canvas.toBlob(resolve,'image/webp',0.84));
      if(!blob)throw new Error('Unable to optimize image.');
      return blob;
    } finally {URL.revokeObjectURL(localURL);}
  }
