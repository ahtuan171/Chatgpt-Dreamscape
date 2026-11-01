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
  const reduceMotion=window.matchMedia('(prefers-reduced-motion: reduce)');
  const petSequences=ASSETS.victor;
  const VICTOR_BOX_WIDTH=74;
  const VICTOR_BOX_HEIGHT=59;

  function positionVictor(){
    if(!victorElement)return;
    if(!settings.enabled||!settings.victor||!composer){victorElement.hidden=true;return;}
    const rect=composer.getBoundingClientRect();
    if(rect.top<0||rect.top>innerHeight||rect.width<200){victorElement.hidden=true;return;}
    victorElement.hidden=false;
    const patrolLimit=Math.min(80,Math.max(22,rect.width*.16));
    const inset=Math.min(16,Math.max(8,rect.width*.025));
    const startX=rect.right-VICTOR_BOX_WIDTH-inset;
    const x=Math.min(innerWidth-VICTOR_BOX_WIDTH,
      Math.max(rect.left,startX-patrolLimit*petTravel));
    const y=Math.max(0,rect.top-VICTOR_BOX_HEIGHT+8);
    victorElement.style.left=Math.round(x)+'px';
    victorElement.style.top=Math.round(y)+'px';
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
    const action=animate?petMotion(now):{mode:'idle',progress:0,facing:'right'};
    const reacted=animate&&Date.now()-lastTyping<900;
    petTravel=action.progress;
    // Typing makes Victor look up; it doesn't make him teleport or run.
    let sequence=action.mode;
    let frame=0;
    if(sequence==='walk')frame=Math.floor(now/210)%petSequences.walk.length;
    else if(sequence==='sleep')frame=Math.floor(now/1700)%petSequences.sleep.length;
    else if(reacted)frame=1;
    else frame=Math.floor(now/3700)%7===0?1:0;
    frame=Math.min(frame,petSequences[sequence].length-1);
    victorElement.dataset.facing=action.facing;
    victorElement.dataset.motion=action.mode;
    drawFrame(sequence,frame,action.facing);
    positionVictor();
  }

  function installVictor(parent){
    victorElement=document.createElement('div');
    victorElement.id='ds-victor';
    victorElement.setAttribute('aria-hidden','true');
    victorElement.hidden=true;
    victorCanvas=document.createElement('canvas');
    victorCanvas.width=VICTOR_BOX_WIDTH*2;
    victorCanvas.height=VICTOR_BOX_HEIGHT*2;
    victorElement.append(victorCanvas);
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
