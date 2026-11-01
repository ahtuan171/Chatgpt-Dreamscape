  // Victor's movement is limited to a small patrol along the right corner of the composer.
  // Preloading and drawing into one fixed canvas avoids sprite-size jitter and ghost images.
  let victorElement=null;
  let victorCanvas=null;
  let victorContext=null;
  let victorImages={};
  let petTimer=null;
  let petStart=performance.now();
  let petTravel=0;
  let lastTyping=0;
  let lastFrameKey='';
  let petReactionUntil=0;
  let petReactionTimer=null;
  const reduceMotion=window.matchMedia('(prefers-reduced-motion: reduce)');
  const petSequences=ASSETS.victor;
  const VICTOR_BOX_WIDTH=74;
  const VICTOR_BOX_HEIGHT=59;

  // Anchor Victor to the model-effort label ("High" in the desktop composer),
  // not the composer's far-right send button. Keep a predictable fallback if the
  // selector changes or a different effort is selected.
  function effortControlRect(composerRect){
    if(!composer)return null;
    const controls=composer.querySelectorAll('button,[role="button"],[data-testid*="model"],span');
    const candidates=[];
    for(const el of controls){
      const label=el.textContent?.replace(/\s+/g,' ').trim().toLowerCase();
      if(!['high','extra high','medium','low','instant','auto','thinking'].includes(label))continue;
      const r=el.getBoundingClientRect();
      if(r.width<8 || r.height<8 || r.width>230 || r.height>95 ||
         r.left<composerRect.left+composerRect.width*.45 ||
         r.right>composerRect.right+10 ||
         r.top<composerRect.top-10 || r.bottom>composerRect.bottom+10)continue;
      const priority=(label==='high'?100:0)+(el.matches('button,[role="button"]')?10:0);
      candidates.push({rect:r,priority});
    }
    candidates.sort((a,b)=>b.priority-a.priority);
    return candidates[0]?.rect||null;
  }

  function positionVictor(){
    if(!victorElement)return;
    if(!settings.enabled||!settings.victor||!composer){victorElement.hidden=true;return;}
    const rect=composer.getBoundingClientRect();
    if(rect.top<0||rect.top>innerHeight||rect.width<200){victorElement.hidden=true;return;}
    victorElement.hidden=false;
    const effort=effortControlRect(rect);
    // Align the cat's middle with the middle of High; if the UI changes,
    // stay toward the right without drifting over the send/microphone buttons.
    const homeCenter=effort?(effort.left+effort.right)/2:
      rect.right-Math.max(105,Math.min(165,rect.width*.18));
    const startX=Math.min(rect.right-VICTOR_BOX_WIDTH-12,
      Math.max(rect.left+12,homeCenter-VICTOR_BOX_WIDTH/2));
    const patrolLimit=Math.min(70,Math.max(20,rect.width*.12));
    const x=Math.min(innerWidth-VICTOR_BOX_WIDTH,
      Math.max(rect.left+8,startX-patrolLimit*petTravel));
    const y=Math.max(0,rect.top-VICTOR_BOX_HEIGHT+8);
    victorElement.style.left=Math.round(x)+'px';
    victorElement.style.top=Math.round(y)+'px';
    victorElement.dataset.anchor=effort?'effort':'fallback';
  }

  function drawFrame(sequence,frame,facing){
    if(!victorContext)return;
    const key=sequence+':'+frame+':'+facing;
    if(key===lastFrameKey)return;
    lastFrameKey=key;
    const image=victorImages[sequence]?.[frame];
    if(!image?.complete||!image.naturalWidth)return;
    const canvas=victorCanvas;
    victorContext.clearRect(0,0,canvas.width,canvas.height);
    const scale=Math.min(5.06,91.08/image.naturalHeight,(canvas.width-8)/image.naturalWidth,(canvas.height-8)/image.naturalHeight);
    const width=Math.round(image.naturalWidth*scale);
    const height=Math.round(image.naturalHeight*scale);
    const x=Math.round((canvas.width-width)/2);
    const y=canvas.height-height-4;
    victorContext.save();
    if(facing==='left'){
      victorContext.translate(canvas.width,0);
      victorContext.scale(-1,1);
    }
    victorContext.drawImage(image,x,y,width,height);
    victorContext.restore();
  }

  // 30-second patrol at the right edge. Face left going out; turn before returning.
  // At the far end Victor rests briefly, turns around, and walks right to his home position.
  function petMotion(now){
    const elapsed=((now-petStart)/1000)%30;
    const smooth=t=>t*t*(3-2*t);
    if(elapsed<5)return {mode:'idle',progress:0,facing:'left'};
    if(elapsed<8)return {mode:'walk',progress:smooth((elapsed-5)/3),facing:'left'};
    if(elapsed<10)return {mode:'idle',progress:1,facing:'left'};
    if(elapsed<11)return {mode:'idle',progress:1,facing:'right'};
    if(elapsed<14)return {mode:'walk',progress:1-smooth((elapsed-11)/3),facing:'right'};
    if(elapsed<22)return {mode:'sleep',progress:0,facing:'right'};
    return {mode:'idle',progress:0,facing:'left'};
  }

  function drawVictor(){
    if(!victorElement)return;
    const animate=settings.enabled&&settings.victor&&settings.motion&&!reduceMotion.matches;
    const now=performance.now();
    const isPetted=now<petReactionUntil;
    const action=isPetted?{mode:'idle',progress:0,facing:'right'}:
      animate?petMotion(now):{mode:'idle',progress:0,facing:'right'};
    const reacted=animate&&Date.now()-lastTyping<900;
    petTravel=action.progress;
    // Typing makes Victor look up; it doesn't make him teleport or run.
    let sequence=action.mode;
    let frame=0;
    if(isPetted)frame=Math.min(1,petSequences.idle.length-1);
    else if(sequence==='walk')frame=Math.floor(now/210)%petSequences.walk.length;
    else if(sequence==='sleep')frame=Math.floor(now/1700)%petSequences.sleep.length;
    else if(reacted)frame=1;
    else frame=Math.floor(now/3700)%7===0?1:0;
    frame=Math.min(frame,petSequences[sequence].length-1);
    victorElement.dataset.facing=action.facing;
    victorElement.dataset.motion=action.mode;
    drawFrame(sequence,frame,action.facing);
    positionVictor();
  }

  function petVictor(){
    if(!settings.enabled||!settings.victor||!victorElement)return;
    petReactionUntil=performance.now()+850;
    // A repeated click restarts the hop without adding another sprite layer.
    victorElement.classList.remove('ds-petted');
    void victorElement.offsetWidth;
    victorElement.classList.add('ds-petted');
    victorElement.dataset.reaction='petted';
    clearTimeout(petReactionTimer);
    petReactionTimer=setTimeout(()=>{
      victorElement?.classList.remove('ds-petted');
      if(victorElement)victorElement.dataset.reaction='idle';
    },850);
    drawVictor();
  }

  function installVictor(parent){
    victorElement=document.createElement('button');
    victorElement.id='ds-victor';
    victorElement.type='button';
    victorElement.setAttribute('aria-label','Pet Victor the pixel cat');
    victorElement.title='Click to pet Victor';
    victorElement.hidden=true;
    victorCanvas=document.createElement('canvas');
    victorCanvas.width=VICTOR_BOX_WIDTH*2;
    victorCanvas.height=VICTOR_BOX_HEIGHT*2;
    victorCanvas.setAttribute('aria-hidden','true');
    victorElement.append(victorCanvas);
    const heart=document.createElement('span');
    heart.className='ds-victor-heart';
    heart.textContent='♥';
    heart.setAttribute('aria-hidden','true');
    victorElement.append(heart);
    victorElement.addEventListener('click',petVictor);
    victorContext=victorCanvas.getContext('2d');
    victorContext.imageSmoothingEnabled=false;
    // Draw into a single high-DPI canvas; the fixed canvas is 15% bigger than v0.3.1.
    // Mirror the sprite for leftward movement; preserve one canvas to avoid ghosting.
    for(const [sequence,frames] of Object.entries(petSequences)){
      victorImages[sequence]=frames.map(src=>{
        const image=new Image();image.src=src;
        image.addEventListener('load',()=>{lastFrameKey='';drawVictor();},{once:true});
        return image;
      });
    }
    parent.append(victorElement);
    const typing=e=>{
      if(e.target?.closest?.('#prompt-textarea,[data-testid="composer-root"] [contenteditable="true"],textarea'))lastTyping=Date.now();
    };
    document.addEventListener('keydown',typing,{passive:true});
    petStart=performance.now();
    petTimer=setInterval(drawVictor,120);
    drawVictor();
  }
