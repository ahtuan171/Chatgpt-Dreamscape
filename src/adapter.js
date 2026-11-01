  // Conservative ChatGPT DOM adapter. Never touches chat message contents.
  let composer=null;
  let observer=null;
  let resizeObserver=null;
  let queued=false;
  let activeDockNodes=[];
  let resizeListener=null;
  function getComposer(){
    for(const selector of [
      '[data-testid="composer-root"]',
      'form:has(#prompt-textarea)',
      'form:has([data-testid="composer-text-input"])',
      'form:has([contenteditable="true"])'
    ]){
      try {
        const el=document.querySelector(selector);
        if(!el)continue;
        const r=el.getBoundingClientRect();
        if(r.width>220 && r.height>28 && r.height<360 && r.top>=0 && r.top<innerHeight) return el;
      }catch{}
    }
    return null;
  }
  function clearDockClasses(){
    for(const e of activeDockNodes)e.classList.remove('ds-dock');
    activeDockNodes=[];
  }
  // Bottom dock wrappers can be replaced or reparented when the composer expands
  // (for example, an image attachment). Do not depend on the composer identity.
  // Mark only compact ancestors around the input: never mark the chat transcript.
  function markDock(el){
    const next=new Set();
    if(el){
      const c=el.getBoundingClientRect();
      let node=el.parentElement;
      let depth=0;
      while(node && depth<18 && node!==document.body && node!==document.documentElement){
        if(node.matches('main,[role="main"],#root,#sidebar,[data-testid="sidebar"]'))break;
        const rect=node.getBoundingClientRect();
        // A real dock can span the full width, but must be near the composer
        // and short enough that it cannot be the whole conversation viewport.
        if(rect.height>Math.max(540,c.height+230) ||
           rect.top<c.top-Math.max(220,c.height+50) ||
           rect.bottom<c.top-8)break;
        next.add(node);
        node=node.parentElement;
        depth++;
      }
      for(const selector of ['#thread-bottom','#thread-bottom-container']){
        const e=document.querySelector(selector);
        if(e&&e.contains(el)){
          const r=e.getBoundingClientRect();
          if(r.height<=Math.max(540,c.height+230) && r.top>=c.top-Math.max(220,c.height+50))next.add(e);
        }
      }
      // Some ChatGPT layouts paint the black gradient in a decorative sibling
      // rather than on a composer ancestor. Only neutralize non-interactive,
      // positioned backdrop layers that overlap the dock; never touch messages.
      for(const wrapper of [...next]){
        for(const sibling of wrapper.children){
          if(sibling===el||sibling.contains(el)||sibling.matches('script,style'))continue;
          const style=getComputedStyle(sibling);
          if(!['absolute','fixed'].includes(style.position))continue;
          if(style.pointerEvents!=='none'&&sibling.getAttribute('aria-hidden')!=='true')continue;
          const r=sibling.getBoundingClientRect();
          if(r.width>=c.width*.9 && r.height>0 &&
             r.height<=Math.max(540,c.height+230) &&
             r.top<c.bottom && r.bottom>c.top-140)next.add(sibling);
        }
      }
    }
    const previous=new Set(activeDockNodes);
    for(const e of previous)if(!next.has(e))e.classList.remove('ds-dock');
    for(const e of next)if(!previous.has(e))e.classList.add('ds-dock');
    activeDockNodes=[...next];
  }
  function syncComposer(){
    queued=false;
    const next=getComposer();
    if(next!==composer){
      if(composer)composer.classList.remove('ds-composer');
      composer=next;
      if(resizeObserver)resizeObserver.disconnect();
      if(composer){composer.classList.add('ds-composer');resizeObserver?.observe(composer);}
    }
    // Expansion/reparenting can change opaque wrappers while keeping the same
    // form element, so rediscover dock ancestors on every scheduled sync.
    markDock(composer);
    positionVictor();
  }
  function scheduleSync(){if(queued)return;queued=true;requestAnimationFrame(syncComposer);}
  function startAdapter(){
    resizeObserver=new ResizeObserver(scheduleSync);
    observer=new MutationObserver(scheduleSync);
    observer.observe(document.body,{childList:true,subtree:true});
    window.addEventListener('resize',scheduleSync,{passive:true});
    window.addEventListener('scroll',scheduleSync,{capture:true,passive:true});
    scheduleSync();
  }
  function stopAdapter(){
    observer?.disconnect();resizeObserver?.disconnect();clearDockClasses();
    composer?.classList.remove('ds-composer');composer=null;
  }
