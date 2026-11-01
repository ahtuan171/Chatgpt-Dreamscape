  // Victor's movement is limited to a small patrol on the left edge of the composer.
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
  const VICTOR_BOX_WIDTH=58;
  const VICTOR_BOX_HEIGHT=46;

  function positionVictor(){
    if(!victorElement)return;
    if(!settings.enabled||!settings.victor||!composer){victorElement.hidden=true;return;}
    const rect=composer.getBoundingClientRect();
    if(rect.top<0||rect.top>innerHeight||rect.width<200){victorElement.hidden=true;return;}
    victorElement.hidden=false;
    const patrolLimit=Math.min(80,Math.max(22,rect.width*.16));
    const startX=rect.left+Math.min(19,Math.max(10,rect.width*.035));
    const x=Math.min(innerWidth-VICTOR_BOX_WIDTH,
      Math.max(0,startX+patrolLimit*petTravel));
    const y=Math.max(0,rect.top-VICTOR_BOX_HEIGHT+8);
    victorElement.style.left=Math.round(x)+'px';
    victorElement.style.top=Math.round(y)+'px';
  }

  function drawFrame(sequence,frame){
    if(!victorContext)return;
    const key=sequence+':'+frame;
    if(key===lastFrameKey)return;
    lastFrameKey=key;
    const image=victorImages[sequence]?.[frame];
    if(!image?.complete||!image.naturalWidth)return;
    const canvas=victorCanvas;
    victorContext.clearRect(0,0,canvas.width,canvas.height);
    const scale=Math.min(4,72/image.naturalHeight);
    const width=Math.round(image.naturalWidth*scale);
    const height=Math.round(image.naturalHeight*scale);
    const x=Math.round((canvas.width-width)/2);
    const y=canvas.height-height-4;
    victorContext.drawImage(image,x,y,width,height);
  }

  // 30-second cycle: watch -> stroll right -> rest -> stroll left -> nap -> watch.
  // Distance is capped at 80 CSS pixels; the animal stays on the left portion.
  function petMotion(now){
    const elapsed=((now-petStart)/1000)%30;
    const smooth=t=>t*t*(3-2*t);
    if(elapsed<5)return {mode:'idle',progress:0};
    if(elapsed<8)return {mode:'walk',progress:smooth((elapsed-5)/3)};
    if(elapsed<11)return {mode:'idle',progress:1};
    if(elapsed<14)return {mode:'walk',progress:1-smooth((elapsed-11)/3)};
    if(elapsed<21)return {mode:'sleep',progress:0};
    return {mode:'idle',progress:0};
  }

  function drawVictor(){
    if(!victorElement)return;
    const animate=settings.enabled&&settings.victor&&settings.motion&&!reduceMotion.matches;
    const now=performance.now();
    const action=animate?petMotion(now):{mode:'idle',progress:0};
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
    drawFrame(sequence,frame);
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
    // Canvas is drawn at 2x native pixel scale for crisp, centered frames.
    // The CSS size is half the backing size, so draw coordinates are 2x.
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
