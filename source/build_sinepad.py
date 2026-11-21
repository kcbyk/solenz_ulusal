#!/usr/bin/env python3
"""Gönderilen Sinepad2 arayüzünü 55 canlı TV kanalı ve gömülü logolarla birleştirir."""
from pathlib import Path
import base64,json,re
ROOT=Path(__file__).resolve().parent
html=(ROOT/'Sinepad2-template.html').read_text(encoding='utf-8')
catalog=json.loads((ROOT/'channels.json').read_text(encoding='utf-8'))['channels']
colors={
 'Ana kanallar':('#39bdf2','#071729'),'Haber':('#f1435b','#220914'),
 'TRT ve kültür':('#d92138','#19070c'),'Spor':('#36cc9f','#08251d'),
 'Eğlence ve müzik':('#af72f8','#190c2d'),'Çocuk':('#fc8a3f','#2b160a'),
 'Kamu':('#68b4f5','#0a1d32'),'Diğer':('#3ee0ff','#071a28'),
}
features={
 'TRT1':('Dizi, haber, spor ve yarışmalarla ulusal genel yayın.','#e11d2e','#2a0509'),
 'ATV':('Diziler, yarışmalar ve ana haber.','#2e8bff','#06182e'),
 'KanalD':('Diziler, magazin ve haber.','#50aaff','#071931'),
 'NOW':('Diziler ve ana haber bülteni.','#8b5cf6','#150a2b'),
 'StarTV':('Diziler, filmler ve eğlence programları.','#f5b400','#2b2105'),
 'TV8':('Yarışma ve eğlence programları.','#ffd23f','#2b2405'),
 'Kanal7':('Dizi, kültür ve genel yayın.','#d71f40','#290814'),
 'ShowTV':('Diziler, eğlence ve ana haber bülteni.','#ff4d6d','#2b0a14'),
}
rows=[]
# Akışın listede olması çalıştığı anlamına gelmez. Tarayıcıda açılmayan Star TV'yi
# veya örnek medya parçası erişilemeyen kaynakları canlı diye göstermiyoruz.
BROWSER_FAILED={'StarTV','NTV','TJKTV','VavTV'}
# Yayıncının çoklu kalite listesi: en düşük varyantla başlar, ABR ağ durumuna göre yükseltir.
# Manifest bulunmayan tek-varyant kanallar mevcut URL ile normal oynatılmaya devam eder.
ADAPTIVE_MASTERS={
 'ATV':'https://rnttwmjcin.turknet.ercdn.net/lcpmvefbyo/atv/atv.m3u8',
 'KanalD':'https://ackaxsqacw.turknet.ercdn.net/ozfkfbbjba/kanald/kanald.m3u8',
 'NOW':'https://uycyyuuzyh.turknet.ercdn.net/nphindgytw/nowtv/nowtv.m3u8',
 'ShowTV':'https://rmtftbjlne.turknet.ercdn.net/bpeytmnqyp/showtv/showtv.m3u8',
 'HTSporTV':'https://rmtftbjlne.turknet.ercdn.net/bpeytmnqyp/ht-spor/ht-spor.m3u8',
 'PowerTV':'https://livetv.powerapp.com.tr/powerTV/powerhd.smil/playlist.m3u8',
 'PowerTurkTV':'https://livetv.powerapp.com.tr/powerturkTV/powerturkhd.smil/playlist.m3u8',
}
for c in catalog:
 ident,name,category=c['id'],c['name'],c['category']
 desc,a,bg=features.get(ident,(f'{category} · Canlı yayın',*colors.get(category,('#3ee0ff','#071a28'))))
 usable=c.get('audit')=='medya_parcasi_eristi' and ident not in BROWSER_FAILED
 direct=c.get('qualityUrl') or c['streamUrl'] or ''
 # Önceden bazı yüksek varyantları oynatmayan kanallarda çalışan temel adresi yedek tut.
 if ident=='BeyazTV':direct=c['streamUrl'] or ''
 if ident=='PowerTurkTV':direct='https://livetv.powerapp.com.tr/powerturkTV/powerturkhd.smil/chunklist_b7596000_sltur.m3u8'
 adaptive=usable and (ident in ADAPTIVE_MASTERS or bool(c.get('qualityUrl') and c['streamUrl'] and c['qualityUrl']!=c['streamUrl']))
 url=(ADAPTIVE_MASTERS.get(ident) or c['streamUrl']) if adaptive else direct if usable else ''
 fallback=direct if adaptive and direct!=url else ''
 quality='Otomatik' if adaptive else ''
 if not usable:desc+=' · Şu an doğrulanmış oynatılabilir yayın yok.'
 elif adaptive:desc+=' · Hızlı başlangıç: kalite bağlantıya göre otomatik yükselir veya düşer.'
 logo=ROOT/'logos'/f'{ident}.png'
 uri='data:image/png;base64,'+base64.b64encode(logo.read_bytes()).decode('ascii') if logo.exists() else ''
 rows.append([ident,name,category,a,bg,url,'',desc,uri,quality,bool(adaptive),fallback])
start=html.index('const CH=[')
end=html.index('const F=CH.map',start)
html=html[:start]+'const CH='+json.dumps(rows,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+';\n'+html[end:]
html=html.replace(
 "const F=CH.map(([id,t,g,a,bg,url,site,syn])=>({id,t,s:'',n:t,g:[g],a,bg,url,site,syn,c:'lg-ch',y:'',m:0,dir:'',cast:''}));",
 "const F=CH.map(([id,t,g,a,bg,url,site,syn,logo,q,adaptive,fallback])=>({id,t,s:'',n:t,g:[g],a,bg,url,site,syn,logo,q,adaptive,fallback,c:'lg-ch',y:'',m:0,dir:'',cast:''}));")
old="const lo=f=>`<div class=\"lo\" style=\"--c1:${f.a};--c2:${f.bg}\">${f.t}</div>`;"
new="const lo=f=>`<div class=\"lo\" style=\"--c1:${f.a};--c2:${f.bg}\">${f.logo?`<img src=\"${f.logo}\" alt=\"\" loading=\"lazy\">`:`<span>${f.t}</span>`}</div>`;"
assert old in html
html=html.replace(old,new)
g0=html.index('const G=[[');g1=html.index('];\nconst $=',g0)+2
icons=[
 ('Tümü','<rect x="4" y="4" width="6" height="6"/><rect x="14" y="4" width="6" height="6"/><rect x="4" y="14" width="6" height="6"/><rect x="14" y="14" width="6" height="6"/>'),
 ('Ana kanallar','<rect x="3" y="6" width="18" height="12" rx="2"/><path d="M8 21h8"/>'),
 ('Haber','<rect x="4" y="5" width="16" height="14" rx="2"/><path d="M8 9h8M8 13h5"/>'),
 ('TRT ve kültür','<path d="M4 16V7l8-4 8 4v9l-8 5z"/><path d="M8 11h8m-8 4h8"/>'),
 ('Spor','<circle cx="12" cy="12" r="8"/><path d="M12 4v16M4 12h16"/>'),
 ('Eğlence ve müzik','<path d="M10 17V5l10-2v12"/><circle cx="7" cy="18" r="3"/><circle cx="17" cy="16" r="3"/>'),
 ('Çocuk','<path d="M12 3l2.4 5.6 6 .6-4.5 4 1.4 6L12 16l-5.3 3.2 1.4-6-4.5-4 6-.6z"/>'),
 ('Kamu','<path d="M3 9l9-6 9 6M5 10v9M10 10v9M14 10v9M19 10v9M3 21h18"/>'),
 ('Diğer','<circle cx="12" cy="12" r="8"/><path d="M12 8v4l3 2"/>')]
html=html[:g0]+'const G='+json.dumps(icons,ensure_ascii=False,separators=(',',':'))+';'+html[g1:]
old="$('#lg').innerHTML=`<h1 class=\"lg ${f.c}\"><span class=\"m\">${f.t}</span>${f.s?`<span class=\"sb2\">${f.s}</span>`:''}</h1>`;"
new="$('#lg').innerHTML=`<h1 class=\"lg ${f.c}\">${f.logo?`<img class=\"hero-logo\" src=\"${f.logo}\" alt=\"${f.t} logosu\">`:`<span class=\"m\">${f.t}</span>`}</h1>`;"
assert old in html
html=html.replace(old,new)
# Çoklu kalite yayınlarında hls.js düşük varyanttan başlar; sonrasında ABR serbesttir.
# Tek varyantlı yayınlarda önceki stabil (yerel HLS öncelikli) oynatım korunur.
old_player='''let hls=null,cur=null,pt=null;
const vdFail=()=>{vd.classList.remove('on');$('#sp').classList.remove('on');if(document.body.classList.contains('pm')){$('#pNh').textContent='Yayın açılamadı';$('#pNp').textContent='Bu kanalın yayın adresi çalışmıyor olabilir. Resmi sitesinde açmayı dene.';$('#pN').style.display='flex'}};
function load(f){
 if(cur===f.id)return !!f.url;
 cur=f.id;if(hls){hls.destroy();hls=null}
 vd.classList.remove('on');vd.removeAttribute('src');vd.load();
 if(!f.url)return false;
 if(window.Hls&&Hls.isSupported()){hls=new Hls({lowLatencyMode:true});hls.loadSource(f.url);hls.attachMedia(vd);hls.on(Hls.Events.ERROR,(_,d)=>{if(d.fatal)vdFail()})}
 else if(vd.canPlayType('application/vnd.apple.mpegurl'))vd.src=f.url;
 else return false;
 vd.play().catch(()=>{});return true}'''
new_player='''let hls=null,cur=null,pt=null,abrTimer=null,nativeRecovery=null;
const vdFail=()=>{vd.classList.remove('on');$('#sp').classList.remove('on');if(document.body.classList.contains('pm')){$('#pNh').textContent='Yayın açılamadı';$('#pNp').textContent='Yayıncı bu akışı sınırlandırmış veya bağlantı kapanmış olabilir.';$('#pN').style.display='flex'}};
function useNative(f){
 if(cur!==f.id)return;
 clearTimeout(abrTimer);
 if(hls){hls.destroy();hls=null}
 nativeRecovery={id:f.id,triedDirect:false};
 vd.pause();vd.removeAttribute('src');vd.load();vd.src=f.url;vd.play().catch(()=>{});
}
// Bazı CDN'ler hls.js için CORS izni vermeyebilir: yerel HLS, gerekirse eski URL.
vd.addEventListener('error',()=>{
 if(!nativeRecovery||cur!==nativeRecovery.id||nativeRecovery.triedDirect)return;
 const f=F.find(x=>x.id===cur);
 if(!f?.fallback||f.fallback===f.url)return;
 nativeRecovery.triedDirect=true;
 vd.pause();vd.removeAttribute('src');vd.load();vd.src=f.fallback;vd.play().catch(()=>{});
});
function load(f){
 if(cur===f.id)return !!f.url;
 clearTimeout(abrTimer);cur=f.id;nativeRecovery=null;
 if(hls){hls.destroy();hls=null}
 vd.pause();vd.classList.remove('on');vd.removeAttribute('src');vd.load();
 if(!f.url)return false;
 if(f.adaptive&&window.Hls&&Hls.isSupported()){
  const instance=new Hls({lowLatencyMode:false,startLevel:0,abrEwmaDefaultEstimate:750000});
  hls=instance;
  instance.on(Hls.Events.ERROR,(_,d)=>{if(d.fatal&&cur===f.id&&hls===instance)useNative(f)});
  instance.attachMedia(vd);instance.loadSource(f.url);
  abrTimer=setTimeout(()=>{if(cur===f.id&&hls===instance&&vd.readyState<2)useNative(f)},13000);
 }else if(vd.canPlayType('application/vnd.apple.mpegurl'))vd.src=f.url;
 else if(window.Hls&&Hls.isSupported()){
  const instance=new Hls({lowLatencyMode:false});hls=instance;
  instance.on(Hls.Events.ERROR,(_,d)=>{if(d.fatal&&cur===f.id&&hls===instance)vdFail()});
  instance.attachMedia(vd);instance.loadSource(f.url);
 }else return false;
 vd.play().catch(()=>{});return true}'''
assert old_player in html
html=html.replace(old_player,new_player)
# Seçili kanalın ana sayfadaki sessiz video önizlemesini geri getir.
# İlk parça düşük kalitede başlar; hls.js bağlantı izin verirse kendiliğinden yükseltir.
html=html.replace("setSel=function(i){_ss(i);clearTimeout(pt);pt=setTimeout(()=>{if(!$('#ov').classList.contains('open'))load(F[i])},500)};", """function schedulePreview(){
 clearTimeout(pt);
 pt=setTimeout(()=>{
  if($('#ov').classList.contains('open')||document.hidden)return;
  const f=F[sel];vd.muted=true;
  if(load(f)){
   vd.play().catch(()=>{});
  }
 },450);
}
setSel=function(i){_ss(i);schedulePreview()};
document.addEventListener('visibilitychange',()=>{
 if(document.hidden&&!$('#ov').classList.contains('open')){clearTimeout(pt);vd.pause()}
 else if(!document.hidden&&!$('#ov').classList.contains('open'))schedulePreview();
});""")
html=html.replace("function stopVid(){document.body.classList.remove('pm');$('#ov').classList.remove('live');vd.muted=true;if(document.fullscreenElement)document.exitFullscreen();clearTimeout(idle)}", "function stopVid(){document.body.classList.remove('pm');$('#ov').classList.remove('live');clearTimeout(abrTimer);clearTimeout(pt);cur=null;nativeRecovery=null;if(hls){hls.destroy();hls=null}vd.pause();vd.removeAttribute('src');vd.load();vd.muted=true;if(document.fullscreenElement)document.exitFullscreen();clearTimeout(idle);schedulePreview()}")
# .m3u8 doğrudan oynatılabiliyorsa ilk videoyu hazırlarken ses kapalı tut.
html=html.replace("$('#pB').style.backgroundImage=`url(${f.img})`;","$('#pB').style.backgroundImage='none';")
html=html.replace("Bu kanalın yayın adresi eklenmedi","Bu kanalın doğrudan yayını bulunamadı")
html=html.replace("Dosyanın başındaki kanal listesine .m3u8 adresini ekleyebilir ya da resmi sitesinde izleyebilirsin.","Bu yayına şu anda doğrudan erişilemiyor. Daha sonra tekrar dene.")
html=html.replace('YAYIN ADRESİ (.m3u8, boşsa "Sitede aç" çıkar), resmi site, açıklama','YAYIN ADRESİ (.m3u8, yoksa kanal geçici olarak kullanılamaz), açıklama')
html=html.replace("Bu film için video yok","Yayın şu anda açılamıyor")
html=html.replace("Bilgisayarındaki bir video dosyasını seç, burada oynatalım. Dosya hiçbir yere yüklenmez.","Bu kanalın doğrulanmış bir canlı yayın adresi bulunamadı.")
html=html.replace("Bu kanalın yayın adresi çalışmıyor olabilir. Resmi sitesinde açmayı dene.","Yayıncı bu akışı sınırlandırmış veya bağlantı kapanmış olabilir.")
# Kullanıcının istemediği dış site düğmeleri ve canlı yayındaki Infinity:NaN:NaN zaman etiketi.
html=html.replace('<button class="ov-b pri" id="pF">Sitede aç</button>','')
html=html.replace('<button class="ov-b" id="pF2">Sitede aç</button>','')
html=re.sub(r'<span id="pTm"[^>]*>.*?</span>','',html)
html=html.replace("$('#pF').focus()","$('#pC').focus()")
html=html.replace(" else if(id==='pF'||id==='pF2')window.open(F[sel].site,'_blank','noopener');\n",'')
html=html.replace("$('#pTm').textContent=fm(vd.currentTime)+' / '+fm(d)","/* Canlı yayında süre etiketi yok */")
html=html.replace("$('#pTm').textContent='● CANLI    ↑↓ kanal    ←→ ses';",'')
html=html.replace('if(d){k.value=vd.currentTime/d*1000;', 'if(Number.isFinite(d)&&d>0){k.value=vd.currentTime/d*1000;')
html=html.replace("$('#chips').innerHTML=[f.g[0],'● CANLI'].map(x=>`<span>${x}</span>`).join('');", "$('#chips').innerHTML=[f.g[0],f.url?'● CANLI':'● ŞU AN YOK',...(f.q?[f.q]:[])].map(x=>`<span>${x}</span>`).join('');")
html=html.replace('<button class="tile" data-z="3" data-i="${i}">','<button class="tile ${F[i].url?\'\':\'unavailable\'}" data-z="3" data-i="${i}">')
html=html.replace('<b>${F[i].g[0]}</b></button>', '<b>${F[i].url?F[i].g[0]:\'ŞU AN YOK\'}</b></button>')
html=html.replace("<script src=\"https://cdnjs.cloudflare.com/ajax/libs/hls.js/1.5.8/hls.min.js\"></script>",'<script>'+ (ROOT/'vendor/hls.min.js').read_text(encoding='utf8').replace('</script','<\\/script')+'</script>')
css='''\n/* Gömülü, çevrimdışı görünür kanal logoları */
.lo{background:linear-gradient(135deg,color-mix(in srgb,var(--c2) 75%,#131d34),var(--c2))}
.lo img{max-width:84%;max-height:78%;width:auto;height:auto;object-fit:contain;filter:drop-shadow(0 5px 14px rgba(0,0,0,.28))}
.lo span{font-size:clamp(18px,2.3vw,32px)}
.hero-logo{display:block;max-width:min(34vw,440px);max-height:min(17vh,150px);width:auto;height:auto;object-fit:contain;object-position:left center;filter:drop-shadow(0 10px 25px rgba(0,0,0,.38))}
.tile.unavailable .lo img{opacity:.56;filter:grayscale(.55)}
.tile.unavailable b{color:#ffbf9f}
@media(max-width:760px){.hero-logo{max-width:58vw;max-height:100px}}
'''
html=html.replace('</style></head><body>',css+'</style></head><body>')
# Üstte kaynak arayüzünü koru; sayfa başlığını açıkça TV olarak güncelle.
html=html.replace('<title>Sinepad</title>','<title>Sinepad · Canlı TV</title>')
assert 'https://cdnjs.cloudflare.com/ajax/libs/hls.js' not in html
assert len(rows)==55
out=ROOT/'Sinepad-TV.html';out.write_text(html,encoding='utf8')
print('Oluşturuldu:',out,'kanal:',len(rows),'boyut:',out.stat().st_size)
