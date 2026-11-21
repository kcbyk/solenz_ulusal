# Solenz Ulusal · Sinepad Android TV

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/kcbyk/solenz_ulusal)

Aynı Sinepad arayüzü hem [**canlı Render sitesinde**](https://solenz-ulusal.onrender.com/), hem de **Android TV APK** içinde kullanılır. 55 kanal/logonun bulunduğu tek kaynak HTML `site/index.html` dosyasıdır; APK bu dosyayı yedek olarak paketler. **APK v0.2.0 ilk açılışta `https://solenz-ulusal.onrender.com/` adresini yükler; sunucuya erişilemiyorsa gömülü kopyaya döner.** Gömülü sayfa için internet gerekmez, canlı yayınlar için gerekir.

## Önce Android TV'de dene

1. [`apk/Solenz-TV-AndroidTV-debug.apk`](apk/Solenz-TV-AndroidTV-debug.apk) dosyasını TV'ye USB ile taşıyıp "Bilinmeyen uygulamaları yükle" izniyle kur; **veya** TV ile aynı yerel ağdaki bilgisayarda ADB kurup `bash scripts/install-tv.sh` (Windows: `scripts\\install-tv.bat`) çalıştır. Varsayılan hedef `192.168.1.103:5555`; TV'nin IP'si/portu farklıysa betiğe argüman ver. TV'de geliştirici seçenekleri ve ADB hata ayıklama açık olmalı. Android 11+ eşleştirme ekranı farklı port gösteriyorsa önce `adb pair 192.168.1.103:<PAIR_PORT>`, ardından `adb connect 192.168.1.103:<DEBUG_PORT>` kullan. Bulut ortamındaki bir makine evdeki `192.168.x.x` IP'sine doğrudan erişemez. Bilinmeyen APK'ları başka kaynaklardan kurma.
2. TV uygulamaları menüsünden **Solenz TV**'yi aç. Seçili kanal ana ekranda **sessiz önizleme**, "İzle" ile oynatıcıda sesli yayın; kumandada yön tuşları, OK ve geri tuşu kullanılır.
3. Varsayılan kaynak hazır **Render sitesi**. Kumandada **MENU/Ayarlar** tuşuyla Render, gömülü yedek veya başka bir HTTPS adresi arasında geçiş yapabilirsin. Bazı kumandalarda MENU tuşu yoktur; uygulama yine varsayılan Render adresini açar. Render'daki sayfa güncellemeleri yeni APK kurmadan gelir; gömülü yedeği güncellemek için APK yeniden derlenmelidir.

Bu dosya **debug imzalı test APK'sıdır**, Play Store için üretim sürümü veya kalıcı güncelleme anahtarı değildir. Yeni debug anahtarıyla yeniden imzalanmış sürümler eski sürümün üzerine yüklenmeyebilir. TV modelinde henüz gerçek cihaz testi yapılmadı: Android System WebView, codec desteği, yayıncı CORS kısıtları ve ağ erişimi modelden modele değişir. TV'de WebView kurulu/etkin değilse uygulama bunu bildirir. Kamuya açık yayın listeleri yayın/marka haklarını vermez.

## Render sitesi (Web Service değil, Static Site)

[https://solenz-ulusal.onrender.com/](https://solenz-ulusal.onrender.com/) **21 Kasım 2026'da HTTP 200 ve aynı HTML içerik karmasıyla doğrulandı**. Chromium'da TRT 1, Show TV ve TV8 ana sayfa sessiz önizlemeleri başlatıldı. `render.yaml` tanımı statik `site/` klasörünü yayımlar; değişikliklerde GitHub üzerinden otomatik deploy ayarını Render hesabından kontrol et.

Render yalnız HTML arayüzünü sunar. Videoları TV yayıncı CDN'lerinden doğrudan alır; Render proxy/CORS/DRM veya coğrafi kısıtı çözmez. Static Site üzerinde `source/server.js` ve `/api/*` çalışmaz; APK/tek HTML için gerekli değildir. Repo ve Render sitesi herkese açıktır; dağıtım haklarını kontrol edin.

## Kaynak, eşitleme, APK derleme

- `source/`: Sinepad üretim betikleri, katalog, logolar, yerel test sunucusu, kaynak/lisans notları.
- `site/index.html`: Render'a yayımlanan ve APK'da birebir kullanılan tek dosyalık site.
- `android-tv/`: Android Studio/Gradle Android TV WebView projesi (Java, minSdk 23, Leanback başlatıcı, D-pad ve geri tuşu).
- `render.yaml`: Render Static Site tanımı.

Değişiklikten sonra kök dizinde:

```bash
python3 scripts/sync_site.py        # source/build_sinepad.py -> site/index.html
cd android-tv
./gradlew :app:assembleDebug       # Android SDK 33 ve JDK 11 gerekir
# Çıktı: app/build/outputs/apk/debug/app-debug.apk
```

`source/refresh.py` veya `source/audit_channels.py` çalıştırılacaksa `requests` gerekir; logoları yenilemek için `pillow` da gerekir. `site/index.html` zaten derlenmiş olduğundan Render tarafında Python/Node kurulumu gerekmiyor. Android Studio ile `android-tv/` klasörünü açabilir, gerekli SDK'yı yükletip APK'yı derleyebilirsin. Üretim sürümü için ayrı ve **gizli tutulan** bir imzalama anahtarı oluşturulmalı; anahtarı veya erişim jetonunu GitHub'a koyma.

Gömülü hls.js Apache-2.0 lisanslıdır (`source/vendor/`); logoların kaynakları `source/logo_sources.json` içinde. Videoların oynatılması yayıncı haklarına, TV codec/WebView desteğine ve CDN erişimine bağlıdır. Desteklenmeyen yayınlar arayüzde "ŞU AN YOK" olarak işaretlenir.
