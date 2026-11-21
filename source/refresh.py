#!/usr/bin/env python3
"""iptv-org TR listesini indir, yalnızca seçilmiş ücretsiz ulusal/tematik kanalları kaydet.
Yalnızca üst seviye HLS manifestini kontrol eder: tarayıcı oynatma ve yayın hakkı garantisi değildir.
"""
import concurrent.futures
import datetime
import json
import re
import urllib.request
import urllib.error
from pathlib import Path
from urllib.parse import urlsplit, urljoin

ROOT = Path(__file__).resolve().parent
SOURCE = 'https://iptv-org.github.io/iptv/countries/tr.m3u'
# Ücretli içerik, tanımadığımız yeniden yayın/worker servisleri, kişisel GitHub proxy'leri ve HTTP IP akışları hariç.
# Bu liste resmi lisans değerlendirmesi değil; ücretsiz/halka açık ağlardan teknik bir seçkidir.
CHANNELS = [
 ('TRT1','TRT 1','Ana kanallar','https://www.tabii.com/tr/watch/live/trt1'),
 ('ATV','atv','Ana kanallar','https://www.atv.com.tr/canli-yayin'),
 ('KanalD','Kanal D','Ana kanallar','https://www.kanald.com.tr/canli-yayin'),
 ('NOW','NOW','Ana kanallar','https://www.nowtv.com.tr/canli-yayin'),
 ('StarTV','Star TV','Ana kanallar','https://www.startv.com.tr/canli-yayin'),
 ('TV8','TV8','Ana kanallar','https://www.tv8.com.tr/canli-yayin'),
 ('Kanal7','Kanal 7','Ana kanallar','https://www.kanal7.com/canli-izle'),
 ('ShowTV','Show TV','Ana kanallar','https://www.showtv.com.tr/canli-yayin'),
 ('TRTHaber','TRT Haber','Haber','https://www.trthaber.com/canli-yayin-izle.html'),
 ('AHaber','A Haber','Haber','https://www.ahaber.com.tr/canli-yayin'),
 ('NTV','NTV','Haber','https://www.ntv.com.tr/canli-yayin/ntv'),
 ('HalkTV','Halk TV','Haber','https://halktv.com.tr/canli-yayin'),
 ('TGRTHaber','TGRT Haber','Haber','https://www.tgrthaber.com/canli-yayin'),
 ('24TV','24 TV','Haber','https://www.yirmidort.tv/canli-yayin'),
 ('FlashHaberTV','Flash Haber','Haber','https://www.flashhabertv.com.tr/'),
 ('IlkeTV','İlke TV','Haber','https://ilketv.com.tr/'),
 ('Ekoturk','Ekotürk','Haber','https://www.ekoturk.com/'),
 ('BloombergHT','Bloomberg HT','Haber','https://www.bloomberght.com/tv'),
 ('CNBCe','CNBC-e','Haber','https://www.cnbce.com/'),
 ('HaberGlobal','Haber Global','Haber','https://haberglobal.com.tr/canli-yayin'),
 ('HaberturkTV','Habertürk','Haber','https://www.haberturk.com/tv'),
 ('CNNTurk','CNN Türk','Haber','https://www.cnnturk.com/tv/canli-yayin'),
 ('Tele1','TELE1','Haber','https://www.tele1.com.tr/canli-yayin'),
 ('TVNET','TVNET','Haber','https://www.tvnet.com.tr/canli-yayin'),
 ('SozcuTV','Sözcü TV','Haber','https://www.sozcu.com.tr/tv/'),
 ('TRT2','TRT 2','TRT ve kültür','https://www.tabii.com/'),
 ('TRTAvaz','TRT Avaz','TRT ve kültür','https://www.trtavaz.com.tr/'),
 ('TRTBelgesel','TRT Belgesel','TRT ve kültür','https://www.trtbelgesel.com.tr/'),
 ('TRTCocuk','TRT Çocuk','TRT ve kültür','https://www.trtcocuk.net.tr/'),
 ('TRTDiyanetCocuk','TRT Diyanet Çocuk','TRT ve kültür','https://www.trtdiyanetcocuk.net.tr/'),
 ('TRTGenc','TRT Genç','TRT ve kültür','https://www.trt.net.tr/'),
 ('TRTKurdi','TRT Kurdî','TRT ve kültür','https://www.trtkurdi.com.tr/'),
 ('TRTMuzik','TRT Müzik','TRT ve kültür','https://www.trtmuzik.net.tr/'),
 ('TRTTurk','TRT Türk','TRT ve kültür','https://www.trtturk.com.tr/'),
 ('TRTSporYildiz','TRT Spor Yıldız','Spor','https://www.trtspor.com.tr/'),
 ('ASpor','A Spor','Spor','https://www.aspor.com.tr/canli-yayin'),
 ('HTSporTV','HT Spor','Spor','https://www.htspor.com/'),
 ('TJKTV','TJK TV','Spor','https://www.tjk.org/'),
 ('TBMMTV','TBMM TV','Kamu','https://www.tbmm.gov.tr/'),
 ('DiyanetTV','Diyanet TV','Kamu','https://diyanet.tv/'),
 ('A2TV','a2','Eğlence ve müzik','https://www.a2tv.com.tr/canli-yayin'),
 ('360','360','Eğlence ve müzik','https://www.tv360.com.tr/'),
 ('TV4','TV4','Eğlence ve müzik','https://www.tv4.com.tr/'),
 ('EuroD','Euro D','Eğlence ve müzik','https://www.eurod.com.tr/'),
 ('DreamTurk','Dream Türk','Eğlence ve müzik','https://www.dreamturk.com.tr/'),
 ('KralPopTV','Kral Pop TV','Eğlence ve müzik','https://www.kralmuzik.com.tr/'),
 ('Number1TV','Number1 TV','Eğlence ve müzik','https://www.numberone.com.tr/'),
 ('PowerTV','Power TV','Eğlence ve müzik','https://www.powerapp.com.tr/'),
 ('PowerTurkTV','PowerTürk TV','Eğlence ve müzik','https://www.powerapp.com.tr/'),
 ('MinikaCocuk','Minika Çocuk','Çocuk','https://www.minikacocuk.com.tr/'),
 ('MinikaGo','Minika Go','Çocuk','https://www.minikago.com.tr/'),
 ('GZT','GZT TV','Diğer','https://www.gzt.com/'),
 ('VavTV','VAV TV','Diğer','https://www.vavtv.com.tr/'),
 ('TGRTBelgesel','TGRT Belgesel','Diğer','https://www.tgrtbelgesel.com.tr/'),
 ('BeyazTV','Beyaz TV','Diğer','https://www.beyaztv.com.tr/canli-yayin'),
]
# Doğrudan yayıncı veya yayın için kullanılan CDN. İstisnalar elle incelenmeli.
HOSTS = (
 'medya.trt.com.tr','daioncdn.net','ercdn.net','duhnet.tv','mncdn.com',
 'mediatriple.net','powerapp.com.tr','ekoturk.net','blutv.com','tgrthaber.com',
 'ilketv.com.tr','tjk.org','fasttvcdn.com',
)
BLOCKED = {'smartplaytv.in', 'ensonhaber.com'}  # üçüncü taraf yansıma: otomatik gömmüyoruz
# Türkiye'deki kamuya açık yayın CDN'lerinden denenmiş adresler. IPTV-org listesinde Show TV yok;
# TV8'in listedeki daioncdn manifesti 200, ancak medya parçaları 401 dönebiliyor;
# Kanal D'nin listedeki adresi ise Chromium'da oynatılamadı. Her yenilemede parçalar sınanır.
MANUAL_STREAMS = {
 'ShowTV':'https://rmtftbjlne.turknet.ercdn.net/bpeytmnqyp/showtv/showtv_1080p.m3u8',
 'TV8':'https://rkhubpaomb.turknet.ercdn.net/fwjkgpasof/tv8/tv8.m3u8',
 'KanalD':'https://ackaxsqacw.turknet.ercdn.net/ozfkfbbjba/kanald/kanald_1080p.m3u8',
 'PowerTurkTV':'https://livetv.powerapp.com.tr/powerturkTV/powerturkhd.smil/playlist.m3u8',
 'BeyazTV':'https://beyaztv-live.daioncdn.net/beyaztv/beyaztv.m3u8',
 'HTSporTV':'https://rmtftbjlne.turknet.ercdn.net/bpeytmnqyp/ht-spor/ht-spor_1080p.m3u8',
 'PowerTV':'https://livetv.powerapp.com.tr/powerTV/powerhd.smil/chunklist_b7596000_sltur.m3u8',
}
DEEP_CHECK = {'TRT1','ATV','KanalD','NOW','StarTV','ShowTV','TV8','TRTHaber','AHaber'}

def get(url, timeout=14):
 request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 CanliTV-demo/1.0'})
 with urllib.request.urlopen(request, timeout=timeout) as response:
  return response.read().decode('utf-8', 'replace')

def parse(text):
 result = {}; info = None
 for raw in text.splitlines():
  line = raw.strip()
  if line.startswith('#EXTINF:'): info = line
  elif line.startswith('#'): continue
  elif line and info:
   m = re.search(r'tvg-id="([^"]+)"', info)
   if m:
    ident = m.group(1).split('.')[0]
    if ident not in result: result[ident] = (line, 'Geo-blocked' in info, 'Not 24/7' in info)
   info = None
 return result

def trusted(url):
 if not url: return False
 p = urlsplit(url)
 host = (p.hostname or '').lower()
 return p.scheme == 'https' and host not in BLOCKED and any(host == h or host.endswith('.'+h) for h in HOSTS) and p.path.endswith('.m3u8')

def probe(item):
 ident,url = item
 if not url: return 'resmi_sayfa'
 try:
  headers={'User-Agent':'Mozilla/5.0','Origin':'http://localhost:3000'}
  def manifest(link):
   with urllib.request.urlopen(urllib.request.Request(link,headers=headers),timeout=9) as resp:
    return resp.read(150000).decode('utf-8','replace'),resp.url
  body,base=manifest(url)
  if not body.startswith('#EXTM3U'):return 'kontrol_edilmeli'
  # Ana kanallar için HLS listesinden bir gerçek medya parçasına da erişmeyi dene.
  if ident in DEEP_CHECK:
   for _ in range(2):
    items=[x.strip() for x in body.splitlines() if x.strip() and not x.startswith('#')]
    if not items:return 'kontrol_edilmeli'
    if '#EXT-X-STREAM-INF' in body:
     body,base=manifest(urljoin(base,items[-1]))
     if not body.startswith('#EXTM3U'):return 'kontrol_edilmeli'
    else:
     with urllib.request.urlopen(urllib.request.Request(urljoin(base,items[0]),headers={**headers,'Range':'bytes=0-31'}),timeout=9) as resp:
      if resp.status not in (200,206) or not resp.read(32):return 'kontrol_edilmeli'
     break
  return 'manifest_erisiyor'
 except Exception:
  return 'kontrol_edilmeli'

def main():
 try:
  source = get(SOURCE)
  found = parse(source)
 except Exception as exc:
  print('Liste alınamadı; mevcut channels.json korunuyor:', exc)
  return
 rows = []
 for ident,name,category,site in CHANNELS:
  raw,geo,intermittent = found.get(ident,(None,False,False))
  url = MANUAL_STREAMS.get(ident) or (raw if trusted(raw) else None)
  if not trusted(url):url = None
  rows.append({'id':ident,'name':name,'category':category,'streamUrl':url,'officialUrl':site,'geoRestricted':geo,'intermittent':intermittent,'status':'bekliyor'})
 with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
  statuses = list(pool.map(probe, ((r['id'],r['streamUrl']) for r in rows)))
 for row,status in zip(rows,statuses):
  row['status']=status
  if row['id'] in MANUAL_STREAMS and status!='manifest_erisiyor':
   row['streamUrl']=None  # doğrulanamayan büyük kanalın resmî sayfası kullanılmalı
   row['status']='resmi_sayfa'
 payload = {'updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':SOURCE,'channels':rows}
 (ROOT/'channels.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 counts={x:statuses.count(x) for x in sorted(set(statuses))}
 print(f'{len(rows)} kanal kaydedildi. {counts}. NOT: manifest erişimi oynatma garantisi değildir.')

if __name__ == '__main__':main()
