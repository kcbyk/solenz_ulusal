#!/usr/bin/env python3
"""Kanal logolarını kaynaklardan indirir, yerel optimize PNG'lere çevirir.
Logolar yayıncıların markalarıdır; IPTV-org veri lisansı marka kullanım izni vermez.
"""
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path
import json, re
import requests
from PIL import Image, ImageOps

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'logos';OUT.mkdir(exist_ok=True)
CAT=json.loads((ROOT/'channels.json').read_text(encoding='utf8'))['channels']
M3U=requests.get('https://iptv-org.github.io/iptv/countries/tr.m3u',timeout=20).text
lines={}
for line in M3U.splitlines():
 if not line.startswith('#EXTINF:'):continue
 m=re.search(r'tvg-id="([^"]+)"',line);l=re.search(r'tvg-logo="([^"]+)"',line)
 if m and l:lines[m.group(1).split('.')[0]]=l.group(1)
logos=requests.get('https://iptv-org.github.io/api/logos.json',timeout=30).json()
bychannel={}
for x in logos:
 if x['in_use'] and x['channel']:
  key=x['channel'].split('.')[0]
  if key not in bychannel:bychannel[key]=x['url']
MANUAL={'FlashHaberTV':ROOT/'manual-logos/FlashHaberTV.png','GZT':ROOT/'manual-logos/GZT.webp'}
REPO='https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/turkey/'
FALLBACK={
 'Ekoturk':'ekoturk-tr.png','TRTAvaz':'trt-avaz-tr.png','TRTBelgesel':'trt-belgesel-tr.png',
 'TRTCocuk':'trt-cocuk-tr.png','TRTKurdi':'trt-kurdi-tr.png','TRTTurk':'trt-turk-tr.png',
 'TRTSporYildiz':'trt-spor-yildiz-tr.png','TBMMTV':'tbmm-tv-tr.png','DiyanetTV':'diyanet-tv-tr.png',
 'AHaber':'a-haber-tr.png','CNNTurk':'cnn-turk-tr.png',
}
SOURCES={}
def save_png(img,path):
 img=ImageOps.exif_transpose(img).convert('RGBA')
 if img.getbbox():img=img.crop(img.getbbox())
 img.thumbnail((440,240),Image.Resampling.LANCZOS)
 canvas=Image.new('RGBA',(440,240),(0,0,0,0));canvas.alpha_composite(img,((440-img.width)//2,(240-img.height)//2))
 canvas.save(path,'PNG',optimize=True)
def one(channel):
 key=channel['id'];path=OUT/(key+'.png')
 if key in MANUAL and MANUAL[key].exists():
  save_png(Image.open(MANUAL[key]),path);return key,'manual-logos/'+MANUAL[key].name,'ok'
 urls=list(dict.fromkeys([lines.get(key),bychannel.get(key),REPO+FALLBACK[key] if key in FALLBACK else None]))
 for url in urls:
  if not url:continue
  try:
   r=requests.get(url,headers={'User-Agent':'Mozilla/5.0 (Sinepad personal project; logo caching)'},timeout=12)
   r.raise_for_status()
   if len(r.content)>4000000:continue
   save_png(Image.open(BytesIO(r.content)),path);return key,url,'ok'
  except Exception:pass
 return key,urls[0] if urls else None,'missing'
with ThreadPoolExecutor(max_workers=12) as e:results=list(e.map(one,CAT))
for key,url,status in results:
 SOURCES[key]={'status':status,'source':url}
 print(key,status,url)
(ROOT/'logo_sources.json').write_text(json.dumps(SOURCES,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Downloaded:',sum(x[2]=='ok' for x in results),'/',len(results))
