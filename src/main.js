  if(window.__DREAMSCAPE_PUBLIC_V1__)return;
  window.__DREAMSCAPE_PUBLIC_V1__=true;
  const style=document.createElement('style');
  style.id='dreamscape-public-style';
  style.textContent=STYLES;
  document.head.append(style);
  function boot(){
    if(!document.body)return;
    installUI();installVictor(interfaceRoot);
    setWallpaperProperties();startAdapter();
    loadCustomWallpapers();
  }
  if(document.body)boot();
  else document.addEventListener('DOMContentLoaded',boot,{once:true});
