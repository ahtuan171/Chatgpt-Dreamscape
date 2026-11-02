  // Conservative ChatGPT DOM adapter. Never touches chat message contents.
  let composer=null;
  let observer=null;
  let resizeObserver=null;
  let queued=false;
  let activeDockNodes=[];
  let resizeListener=null;
  function getComposer(){
    // ChatGPT may render a centered composer on New Chat and a fixed dock in a
    // conversation. Some builds also leave an invisible, older composer mounted.
    // Search ALL candidates, rather than letting a hidden first match block us.
    const visibleRect=el=>{
      if(!el||!el.isConnected)return null;
      const r=el.getBoundingClientRect();
      if(r.width<220||r.height<29||r.height>620 ||r.bottom<=0||
         r.top>=innerHeight||r.right<=0||r.left>=innerWidth)return null;
      const s=getComputedStyle(el);
      if(s.display==='none'||s.visibility==='hidden')return null;
      return r;
    };
    const visibleEditable=el=>{
      if(!el)return false;
      const r=el.getBoundingClientRect();
      const style=getComputedStyle(el);
      return style.display!=='none'&&style.visibility!=='hidden'&&
        r.width>=18&&r.height>=10&&r.bottom>0&&r.top<innerHeight;
    };
    const editorSelector='#prompt-textarea,[data-testid="composer-text-input"],[contenteditable="true"][role="textbox"],textarea';
    const candidates=[];
    for(const selector of [
      '[data-testid="composer-root"]',
      'form:has(#prompt-textarea)',
      'form:has([data-testid="composer-text-input"])',
      'form:has([contenteditable="true"])'
    ]){
      for(const el of document.querySelectorAll(selector)){
        const rect=visibleRect(el);
        if(!rect||!Array.from(el.querySelectorAll(editorSelector)).some(visibleEditable))continue;
        if(!candidates.some(c=>c.element===el))candidates.push({element:el,rect});
      }
    }
    // The New Chat landing can use a div-based composer with no form/testid.
    // Find a compact wrapper around a visible textbox AND its controls.
    if(!candidates.length){
      for(const editor of document.querySelectorAll(editorSelector)){
        if(!visibleEditable(editor))continue;
        let node=editor.parentElement;
        for(let depth=0;node&&depth<7;node=node.parentElement,depth++){
          if(node.matches('#root,main,[role="main"],body'))break;
          const rect=visibleRect(node);
          if(rect&&node.querySelector('button,[role="button"]')){
            candidates.push({element:node,rect});break;
          }
        }
      }
    }
    // Prefer a dock near the bottom if more than one composer is genuinely
    // visible; otherwise use the centered new-chat composer.
    candidates.sort((a,b)=>b.rect.bottom-a.rect.bottom);
    return candidates[0]?.element||null;
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
    observer=new MutationObserver(mutations=>{
      // SPA transitions can reveal a composer by changing CSS alone. Ignore
      // Dreamscape's own position/style mutations to prevent an update loop.
      if(mutations.some(m=>{
        const target=m.target;
        if(target instanceof Element && (target.id==='ds-victor'||target.closest('#dreamscape-app')))return false;
        return true;
      }))scheduleSync();
    });
    observer.observe(document.body,{childList:true,subtree:true,
      attributes:true,attributeFilter:['class','style','hidden','aria-hidden']});
    window.addEventListener('resize',scheduleSync,{passive:true});
    window.addEventListener('scroll',scheduleSync,{capture:true,passive:true});
    scheduleSync();
  }
  function stopAdapter(){
    observer?.disconnect();resizeObserver?.disconnect();clearDockClasses();
    composer?.classList.remove('ds-composer');composer=null;
  }
