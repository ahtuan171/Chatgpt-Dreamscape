"""Generate seven original low-contrast dark desktop wallpapers for Dreamscape.
No third-party artwork or copied characters are used.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np, math, random, json

OUT=Path(__file__).resolve().parents[1]/'assets/wallpapers'
W,H=800,450

def rgb(hexstr):return tuple(bytes.fromhex(hexstr.lstrip('#')))
def col(c,alpha=255):return rgb(c)+(alpha,)
def scene(top,bot,seed,grain=1.65):
    rng=np.random.default_rng(seed)
    y=np.linspace(0,1,H)[:,None,None]
    a=np.array(rgb(top),dtype=np.float32)[None,None,:]
    b=np.array(rgb(bot),dtype=np.float32)[None,None,:]
    arr=np.tile(a*(1-y)+b*y,(1,W,1))
    noise=rng.normal(0,grain,(H,W,1))
    arr=np.clip(arr+noise,0,255).astype(np.uint8)
    return Image.fromarray(arr,'RGB').convert('RGBA')
def glow(im,x,y,r,color,opacity=0.45):
    lay=Image.new('RGBA',(W,H)); d=ImageDraw.Draw(lay)
    rr=rgb(color)
    for rad,alpha in [(r,.012),(r*.7,.025),(r*.4,.048),(r*.18,.10)]:
        rd=int(rad);d.ellipse((x-rd,y-rd,x+rd,y+rd),fill=rr+(int(255*opacity*alpha*8),))
    blurred=lay.filter(ImageFilter.GaussianBlur(int(r*.16)))
    im.alpha_composite(blurred)
def stars(im,seed,count=125,colors=('#94a8c8','#bcb6d2','#c1a375'),area=(0,0,W,H*.83),alpha=(65,180)):
    r=random.Random(seed); layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer)
    x1,y1,x2,y2=area
    for i in range(count):
        x=r.randint(int(x1),int(x2)-1); y=r.randint(int(y1),int(y2)-1)
        color=rgb(r.choice(colors))+(r.randint(*alpha),)
        d.point((x,y),fill=color)
        if i%23==0:
            d.line((x-2,y,x+2,y),fill=color,width=1);d.line((x,y-2,x,y+2),fill=color,width=1)
    im.alpha_composite(layer)
def crescent(im,x,y,r,shade='#e5c99a',cut='#071023'):
    d=ImageDraw.Draw(im);d.ellipse((x-r,y-r,x+r,y+r),fill=rgb(shade)+(220,));d.ellipse((x-r+int(r*.44),y-r-int(r*.15),x+r+int(r*.44),y+r-int(r*.15)),fill=rgb(cut)+(255,))
def mist(im,seed,base=320,color='#3a5475',alpha=30):
    r=random.Random(seed);lay=Image.new('RGBA',(W,H));d=ImageDraw.Draw(lay)
    for j in range(6):
        y=base+j*17+r.randint(-6,6); xx=r.randrange(-120,300)
        d.ellipse((xx,y,xx+r.randrange(260,590),y+20),fill=rgb(color)+(alpha,))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(14)))
def ridgeline(im,seed,start,color,amp=35,frequency=0.012):
    r=random.Random(seed);offset=r.uniform(0,5)
    points=[(x,int(start+math.sin(x*frequency+offset)*amp+math.sin(x*.029+offset*1.7)*amp*.22)) for x in range(-4,W+6,3)]
    points.extend([(W+3,H+2),(-4,H+2)])
    ImageDraw.Draw(im).polygon(points,fill=col(color))
def pine(d,x,y,h,color):
    d.polygon([(x,y-h),(x-h*.23,y-h*.25),(x+h*.23,y-h*.25)],fill=color)
    d.polygon([(x,y-h*.83),(x-h*.31,y-h*.05),(x+h*.31,y-h*.05)],fill=color)
    d.rectangle((x-2,y-h*.08,x+2,y+3),fill=color)
def blocky_clouds(im,seed,y_range=(80,220),num=6,color='#1c3155'):
    r=random.Random(seed); d=ImageDraw.Draw(im)
    for i in range(num):
        x=r.randint(-55,W-45);y=r.randint(*y_range);tw=r.randint(62,130)
        for j in range(7):
            ww=r.randint(7,25);xx=x+j*(tw//7);yy=y-r.randint(0,10)+abs(3-j)*3
            d.rectangle((xx,yy,xx+ww,yy+r.randint(2,6)),fill=col(color,165))
def water(im,seed,horizon=365,reflection_color='#60779f'):
    rng=random.Random(seed);d=ImageDraw.Draw(im)
    for _ in range(250):
        x=rng.randrange(0,W);y=rng.randrange(horizon,H)
        width=rng.randrange(3,25)
        d.line((x,y,x+width,y),fill=(*rgb(reflection_color),rng.randint(14,65)),width=1)
def finish(im,filename):
    # A gentle dark edge vignette preserves contrast and keeps bright details away from the reading column.
    ary=np.asarray(im.convert('RGB')).astype(np.float32)
    yy,xx=np.ogrid[:H,:W]
    dx=np.abs(xx-W/2)/(W/2);dy=np.abs(yy-H*.48)/(H*.52)
    vig=np.clip(.97-.10*(dx*dx+dy*dy),.78,1)
    ary=(ary*vig[:,:,None]).clip(0,255).astype(np.uint8)
    out=Image.fromarray(ary).resize((1600,900),Image.Resampling.NEAREST)
    out.save(OUT/filename,'WEBP',quality=85,method=6)
    return out

# 1: Luminous Garden — quiet cyan flora placed at far edges/bottom.
im=scene('#060c12','#0b2027',211,1.2); stars(im,11,30,colors=('#2f778d','#659aa5'),alpha=(25,75))
glow(im,120,335,105,'#12cbe0',.7);glow(im,690,385,90,'#22aec5',.6)
d=ImageDraw.Draw(im)
for i,(x,y,h) in enumerate([(86,395,128),(139,389,94),(675,428,104),(732,424,65),(47,426,76),(601,438,61)]):
    d.line((x,y,x+int(h*.03),y-h),fill=col('#1a7177',210),width=3)
    for shift in [-1,1]:
        d.polygon([(x,y-20),(x+shift*18,y-33),(x+shift*36,y-35),(x+shift*14,y-16)],fill=col('#11515b'))
    flower= '#50d5e0' if i%2==0 else '#6dabc8'
    d.polygon([(x-9,y-h-2),(x-11,y-h-14),(x-3,y-h-23),(x+6,y-h-20),(x+12,y-h-11),(x+9,y-h-2)],fill=col(flower))
    d.rectangle((x-4,y-h-20,x+3,y-h-6),fill=col('#b5f6f4'))
for j in range(75):
    r=random.Random(911+j);x=r.randrange(W);y=r.randrange(240,440)
    if 180<x<595:continue
    d.rectangle((x,y,x+1,y+1),fill=col('#387d84',r.randint(50,130)))
finish(im,'luminous-garden.webp')

# 2: Night Forest — deep navy with distant silver moon and silhouettes along the lower edge.
im=scene('#080b17','#101c29',304);stars(im,31,95,alpha=(40,135));crescent(im,680,96,30,'#cad2c5','#080e1b')
blocky_clouds(im,66,(110,180),5,'#1c2d48');ridgeline(im,6,340,'#0e2230',25);ridgeline(im,43,377,'#091722',17)
d=ImageDraw.Draw(im)
r=random.Random(81)
for i in range(125):
    x=r.randrange(W); y=r.randrange(392,480);h=r.randrange(16,76)
    if 270<x<530:h=int(h*.55)
    pine(d,x,y,h,col(r.choice(['#09141d','#0a1822','#0b1c25'])))
for j in range(22):
    x=r.randrange(W);y=r.randrange(290,425)
    if 250<x<550:continue
    d.ellipse((x-1,y-1,x+2,y+2),fill=col('#8bc1bc',90))
finish(im,'starlit-forest.webp')

# 3: Violet city — glowing skyline around the bottom half, low center brightness.
im=scene('#0e0c28','#151034',105);stars(im,107,90,colors=('#826bc0','#afb5e3','#c4a9f5'));crescent(im,150,91,26,'#b8a7f9','#100d2a')
d=ImageDraw.Draw(im); r=random.Random(123)
for x in range(-15,W,19):
    height=r.randint(75,168);height+=int(32*max(0,abs(x-W/2)/(W/2)-.1))
    y=420-height;w=r.randint(14,25);color=r.choice(['#1c1940','#1b214e','#221a51','#252254'])
    d.rectangle((x,y,x+w,443),fill=col(color))
    for wy in range(y+10,420,11):
        for wx in range(x+4,x+w-2,7):
            if r.random()<.37: d.rectangle((wx,wy,wx+1,wy+3),fill=col(r.choice(['#6e75c1','#a59bd8','#d5a6bd']),r.randint(100,190)))
d.rectangle((0,421,W,450),fill=col('#0b0b21'))
for x in range(16,W,110): d.line((x,419,x+55,419),fill=col('#534b83'),width=1)
finish(im,'violet-city.webp')

# 5: Golden wildflowers — luminous blooms against darkness, edges only.
im=scene('#0b0c10','#15120f',883,.8);glow(im,88,360,107,'#ad9067',.56);glow(im,690,370,118,'#8c664c',.55)
d=ImageDraw.Draw(im);r=random.Random(8)
for j in range(90):
    side=r.choice([0,1]);x=r.randrange(0,205) if side==0 else r.randrange(595,W)
    y=r.randrange(370,510);h=r.randrange(24,112)
    d.line((x,y,x+r.randrange(-16,16),y-h),fill=col(r.choice(['#45402b','#383c2e','#323826']),r.randrange(65,140)),width=1)
    if j%4==0:
        for a in range(0,360,60):
            fx=x+math.cos(math.radians(a))*r.randrange(3,10)
            fy=y-h+math.sin(math.radians(a))*r.randrange(3,10)
            d.ellipse((fx-2,fy-2,fx+2,fy+2),fill=col(r.choice(['#bda37d','#caba9d','#806647']),r.randrange(75,165)))
finish(im,'golden-wildflowers.webp')

# 6: Quiet library — dark desk objects at corners, lots of empty center.
im=scene('#0b0d11','#1b191b',999,1.1)
d=ImageDraw.Draw(im)
# diffuse desk lower edge and vintage book far left
for t in range(70):
    y=379+t; d.line((0,y,W,y),fill=col('#151217',min(255,130+t)),width=1)
d.polygon([(10,362),(165,347),(245,409),(82,436)],fill=col('#3a3434'))
d.line((18,371,165,355,233,407),fill=col('#8c7f76',160),width=2)
for k in range(14):
    yy=371+k*3;d.line((53,yy,181,yy-12),fill=col('#8b8277',35),width=1)
# cup lower right
r=Image.new('RGBA',(W,H));rd=ImageDraw.Draw(r)
rd.ellipse((658,341,757,371),fill=col('#494247'))
rd.ellipse((670,351,746,370),fill=col('#16151b'))
rd.ellipse((687,357,735,367),fill=col('#0e0d13'))
rd.ellipse((732,348,775,380),outline=col('#a59b91'),width=4)
rd.rectangle((670,357,746,409),fill=col('#45424c'))
rd.polygon([(670,402),(746,402),(730,419),(681,419)],fill=col('#33303d'))
r=r.filter(ImageFilter.GaussianBlur(.35));im.alpha_composite(r)
glow(im,675,384,98,'#a98e72',.26)
finish(im,'quiet-library.webp')

# 7: Chess at night — tiny white pawn and queen mirrored, mostly charcoal void.
im=scene('#08090e','#101116',78,.7)
d=ImageDraw.Draw(im)
d.ellipse((97,376,265,410),fill=col('#26272e',165))
# board, lower-left only
d.polygon([(0,402),(301,382),(354,450),(0,450)],fill=col('#1e1f24'))
for i in range(7):d.line((i*55,390,i*62,450),fill=col('#777984',35),width=1)
for i in range(3):d.line((0,405+i*15,340,396+i*17),fill=col('#6a6d79',32),width=1)
# pawn
x,y=166,396
d.ellipse((x-15,y-68,x+15,y-39),fill=col('#b4b6b9',215));d.polygon([(x-11,y-44),(x+11,y-44),(x+17,y-15),(x-17,y-15)],fill=col('#999aa4'))
d.ellipse((x-25,y-16,x+25,y-4),fill=col('#b6b5bb'));d.rectangle((x-29,y-5,x+29,y),fill=col('#9b9ca5'))
# reflection (barely visible), tall queen on far right subtle
d.ellipse((658,397,725,409),fill=col('#3d3b45',155))
d.polygon([(676,397),(709,397),(701,329),(682,329)],fill=col('#626471',125))
d.polygon([(674,329),(682,308),(693,319),(704,306),(712,329)],fill=col('#858591',135))
finish(im,'chess-at-night.webp')

# 8: Midnight piano — restrained stage spotlight, piano near bottom-right.
im=scene('#07080d','#0c0c12',12,.65)
glow(im,617,355,174,'#b8b0a6',.30)
d=ImageDraw.Draw(im)
# beam with extremely soft opacity at right; black silhouette at bottom right
lay=Image.new('RGBA',(W,H));ld=ImageDraw.Draw(lay)
ld.polygon([(578,15),(626,15),(745,429),(458,429)],fill=col('#c2c2bd',9))
im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(24)))
d=ImageDraw.Draw(im)
d.ellipse((480,414,750,432),fill=col('#525157',85))
d.polygon([(514,339),(676,331),(728,364),(704,382),(508,372)],fill=col('#4b4d57'))
d.polygon([(521,337),(676,326),(666,340),(531,354)],fill=col('#a2a5a7',150))
d.polygon([(514,353),(704,368),(704,389),(518,377)],fill=col('#26262d'))
d.line((548,372,548,421),fill=col('#535158'),width=5)
d.line((677,379,680,423),fill=col('#535158'),width=5)
d.rectangle((586,389,632,396),fill=col('#616166'))
d.line((600,393,600,421),fill=col('#494b50'),width=4);d.line((620,393,620,420),fill=col('#494b50'),width=4)
finish(im,'piano-nocturne.webp')

manifest=OUT/'manifest.json'
items=[x for x in json.loads(manifest.read_text()) if x["id"] in ("moonlit-village","moonlit-castle","midnight-tulips")]
items.extend([
 {'id':'luminous-garden','name':'Luminous Garden','dim':10,'file':'assets/wallpapers/luminous-garden.webp'},
 {'id':'starlit-forest','name':'Starlit Forest','dim':12,'file':'assets/wallpapers/starlit-forest.webp'},
 {'id':'violet-city','name':'Violet City','dim':20,'file':'assets/wallpapers/violet-city.webp'},
 {'id':'golden-wildflowers','name':'Golden Wildflowers','dim':8,'file':'assets/wallpapers/golden-wildflowers.webp'},
 {'id':'quiet-library','name':'Quiet Library','dim':10,'file':'assets/wallpapers/quiet-library.webp'},
 {'id':'chess-at-night','name':'Chess at Night','dim':6,'file':'assets/wallpapers/chess-at-night.webp'},
 {'id':'piano-nocturne','name':'Piano Nocturne','dim':7,'file':'assets/wallpapers/piano-nocturne.webp'},
])
manifest.write_text(json.dumps(items,indent=2)+'\n')
print('Generated',len(items),'total wallpapers')
