  let victorElement=null;
  let petTimer=null;
  let petPhase=0;
  let lastTyping=0;
  let petState='idle';
  let petFrame=-1;
  const reduceMotion=window.matchMedia('(prefers-reduced-motion: reduce)');
  const petSequences=ASSETS.victor;
  function positionVictor(){
    if(!victorElement)return;
    if(!settings.enabled||!settings.victor||!composer){victorElement.hidden=true;return;}
    const rect=composer.getBoundingClientRect();
    if(rect.top<0||rect.top>innerHeight||rect.width<200){victorElement.hidden=true;return;}
    victorElement.hidden=false;
    const size=48;
    const x=Math.min(innerWidth-size,Math.max(0,rect.left+Math.min(84,rect.width*.15)));
    const y=Math.max(0,rect.top-39);
    victorElement.style.left=Math.round(x)+'px';
    victorElement.style.top=Math.round(y)+'px';
  }
  function drawVictor(){
    if(!victorElement)return;
    const playing=settings.enabled&&settings.victor&&settings.motion&&!reduceMotion.matches;
    const t=Date.now();
    let next='idle';
    if(playing){
      if(t-lastTyping<950) next='walk';
      else if(petPhase%125>101)next='sleep';
      else if(petPhase%125>80)next='walk';
    }
    const seq=petSequences[next];
    const frame=playing?Math.floor(petPhase/(next==='walk'?2:6))%seq.length:0;
    if(next!==petState || frame!==petFrame){
      victorElement.src=seq[frame];
      petState=next;petFrame=frame;
    }
    if(settings.motion&&playing)petPhase++;
    positionVictor();
  }
  function installVictor(parent){
    victorElement=document.createElement('img');
    victorElement.id='ds-victor';
    victorElement.alt='';victorElement.setAttribute('aria-hidden','true');
    victorElement.draggable=false;victorElement.hidden=true;
    parent.append(victorElement);
    const typing=e=>{
      const target=e.target;
      if(target?.closest?.('#prompt-textarea,[data-testid="composer-root"] [contenteditable="true"],textarea'))lastTyping=Date.now();
    };
    document.addEventListener('keydown',typing,{passive:true});
    petTimer=setInterval(drawVictor,360);
    drawVictor();
  }
