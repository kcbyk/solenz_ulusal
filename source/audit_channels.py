#!/usr/bin/env python3
"""Ücretsiz akışları manifest + örnek medya parçası ile kontrol eder; sabit en yüksek varyantı seçer.
Bu doğrulama tarayıcı/konum/lisans garantisi değildir. Kontrol sonucu channels.json'a yazılır.
"""
import concurrent.futures,datetime,json,re
from pathlib import Path
from urllib.parse import urljoin,urlsplit,parse_qs
import requests
ROOT=Path(__file__).resolve().parent
p=ROOT/'channels.json';data=json.loads(p.read_text(encoding='utf8'))
HEAD={'User-Agent':'Mozilla/5.0','Origin':'http://localhost:3000'}
VOLATILE={'sid','st','e','token','expires','nimblesessionid','auth','hdnea','hdnts'}
def variants(text,base):
 ls=text.splitlines();found=[]
 for i,line in enumerate(ls):
  if not line.startswith('#EXT-X-STREAM-INF:'):continue
  nxt=next((x.strip() for x in ls[i+1:] if x.strip() and not x.startswith('#')),None)
  if not nxt:continue
  res=re.search(r'RESOLUTION=(\d+)x(\d+)',line,re.I)
  bw=re.search(r'(?<!AVERAGE-)BANDWIDTH=(\d+)',line,re.I)
  found.append((int(res.group(1))*int(res.group(2)) if res else 0,int(bw.group(1)) if bw else 0,urljoin(base,nxt)))
 return sorted(found,reverse=True)
def check(c):
 u=c['streamUrl'];result={'id':c['id'],'qualityUrl':None,'maxResolution':None,'audit':'resmi_sayfa' if not u else 'kontrol_edilmeli'}
 if not u:return result
 try:
  with requests.get(u,headers=HEAD,timeout=9) as r:
   r.raise_for_status();text=r.text
   if not text.startswith('#EXTM3U'):return result
   v=variants(text,r.url)
   for _,__,url in (v or [(0,0,u)]):
    try:
     with requests.get(url,headers=HEAD,timeout=9) as media:
      media.raise_for_status();s=media.text
      if not s.startswith('#EXTM3U'):
       continue
      items=[x.strip() for x in s.splitlines() if x.strip() and not x.startswith('#')]
      if not items:continue
      # yalnızca küçük aralık: büyük video dosyasını indirmiyoruz
      with requests.get(urljoin(media.url,items[0]),headers={**HEAD,'Range':'bytes=0-187'},timeout=9,stream=True) as seg:
       if seg.status_code not in (200,206):continue
       part=next(seg.iter_content(188),b'')
       if not part or part[:1]==b'<':continue
       if urlsplit(urljoin(media.url,items[0])).path.endswith('.ts') and part[:1]!=b'G':continue
      result['audit']='medya_parcasi_eristi'
      # geçici imzalı varyantı JSON'a sabitlemeyiz; bir gün sonra çalışmaz.
      if v and not VOLATILE.intersection(parse_qs(urlsplit(url).query)):
       result['qualityUrl']=url
      match=re.search(r'(\d{3,4})x(\d{3,4})',urlsplit(url).path.rsplit('/',1)[-1])
      chosen=next((x for x in v if x[2]==url),None)
      if chosen and chosen[0]>0:
       h=round((chosen[0]*9/16)**.5)
       result['maxResolution']=f'{round(h*16/9)}x{h}'
      elif match:result['maxResolution']=match.group(0)
      else:
       m=re.search(r'(1440|1080|720|576|480|360)p?',urlsplit(url).path.rsplit('/',1)[-1])
       if m:result['maxResolution']=m.group(1)+'p'
      return result
    except Exception:continue
   result['audit']='manifest_var_medya_yok' if v or '#EXT-X-MEDIA-SEQUENCE' in text else 'kontrol_edilmeli'
 except Exception:pass
 return result
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
 results=list(pool.map(check,data['channels']))
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
for c,r in zip(data['channels'],results):
 c.update({k:v for k,v in r.items() if k!='id'})
 c['lastCheckedAt']=now
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for c in data['channels']:
 print(f"{c['name']:<23} {c['audit']:<26} {str(c['maxResolution']):<12} {c['qualityUrl'] or ''}")
from collections import Counter
print('ÖZET:',dict(Counter(c['audit'] for c in data['channels'])))
