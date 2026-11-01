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
  function markDock(el){
    clearDockClasses();
    if(!el)return;
    let node=el.parentElement;
    const c=el.getBoundingClientRect();
    let depth=0;
    while(node && depth<8 && node!==document.body && node!==document.documentElement){
      if(node.matches('main,[role="main"],#root,#sidebar,[data-testid="sidebar"]'))break;
      const rect=node.getBoundingClientRect();
      // Limit transparency to short composer wrappers, never chat turns or large panels.
      if(rect.height>Math.max(420,c.height+150) || rect.top<c.top-180) break;
      node.classList.add('ds-dock');activeDockNodes.push(node);
      node=node.parentElement;depth++;
    }
    for(const selector of ['#thread-bottom','#thread-bottom-container']){
      const e=document.querySelector(selector);
      if(e && e.contains(el) && !activeDockNodes.includes(e)){
        e.classList.add('ds-dock');activeDockNodes.push(e);
      }
    }
  }
  function syncComposer(){
    queued=false;
    const next=getComposer();
    if(next!==composer){
      if(composer)composer.classList.remove('ds-composer');
      composer=next;
      if(resizeObserver)resizeObserver.disconnect();
      if(composer){composer.classList.add('ds-composer');resizeObserver?.observe(composer);}
      markDock(composer);
    }
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
