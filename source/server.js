// Bağımlılıksız demo sunucusu: yayınları proxy'lemez, yalnızca katalog/arayüz sunar.
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const ROOT = __dirname;
const PORT = Number(process.env.PORT || 3000);
const send = (res, status, type, body) => {
  res.writeHead(status, {'Content-Type': type, 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff'});
  res.end(body);
};
http.createServer((req, res) => {
  const pathname = new URL(req.url, 'http://localhost').pathname;
  try {
    if (pathname === '/vendor/hls.min.js') return send(res, 200, 'text/javascript; charset=utf-8', fs.readFileSync(path.join(ROOT,'vendor/hls.min.js')));
    if (pathname === '/api/channels') return send(res, 200, 'application/json; charset=utf-8', fs.readFileSync(path.join(ROOT,'channels.json')));
    if (pathname === '/api/playlist.m3u') {
      const data = JSON.parse(fs.readFileSync(path.join(ROOT,'channels.json'),'utf8'));
      const lines = ['#EXTM3U'];
      const browserFailed = new Set(['StarTV','NTV','TJKTV','VavTV']);
      const adaptiveMasters = {
        ATV:'https://rnttwmjcin.turknet.ercdn.net/lcpmvefbyo/atv/atv.m3u8',
        KanalD:'https://ackaxsqacw.turknet.ercdn.net/ozfkfbbjba/kanald/kanald.m3u8',
        NOW:'https://uycyyuuzyh.turknet.ercdn.net/nphindgytw/nowtv/nowtv.m3u8',
        ShowTV:'https://rmtftbjlne.turknet.ercdn.net/bpeytmnqyp/showtv/showtv.m3u8',
        HTSporTV:'https://rmtftbjlne.turknet.ercdn.net/bpeytmnqyp/ht-spor/ht-spor.m3u8',
        PowerTV:'https://livetv.powerapp.com.tr/powerTV/powerhd.smil/playlist.m3u8',
        PowerTurkTV:'https://livetv.powerapp.com.tr/powerturkTV/powerturkhd.smil/playlist.m3u8'
      };
      for (const channel of data.channels) {
        if (channel.audit !== 'medya_parcasi_eristi' || browserFailed.has(channel.id)) continue;
        const adaptive = adaptiveMasters[channel.id] ||
          (channel.qualityUrl && channel.streamUrl && channel.qualityUrl !== channel.streamUrl ? channel.streamUrl : null);
        // M3U uygulamasının kendi adaptif kalite desteğine bağlıdır.
        const url = adaptive || (channel.id === 'BeyazTV' ? channel.streamUrl : channel.qualityUrl || channel.streamUrl);
        if (!url) continue;
        lines.push(`#EXTINF:-1 tvg-id="${channel.id}.tr" group-title="${channel.category}",${channel.name}`, url);
      }
      return send(res, 200, 'application/x-mpegURL; charset=utf-8', lines.join('\n')+'\n');
    }
    if (pathname === '/' || pathname === '/Sinepad-TV.html') return send(res, 200, 'text/html; charset=utf-8', fs.readFileSync(path.join(ROOT,'Sinepad-TV.html')));
    if (pathname === '/index.html' || pathname === '/classic') return send(res, 200, 'text/html; charset=utf-8', fs.readFileSync(path.join(ROOT,'index.html')));
    return send(res, 404, 'text/plain; charset=utf-8', 'Not found');
  } catch (e) {
    console.error(e);
    return send(res, 500, 'text/plain; charset=utf-8', 'Katalog okunamadı; python refresh.py komutunu çalıştırın.');
  }
}).listen(PORT,'0.0.0.0',()=>console.log(`Canlı TV demo: http://0.0.0.0:${PORT}`));
