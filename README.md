# Solenz Ulusal · Sinepad Android TV

Aynı Sinepad arayüzü hem **Render Static Site** üzerinde, hem de **Android TV APK** içinde kullanılır. 55 kanal/logonun bulunduğu tek kaynak HTML `site/index.html` dosyasıdır; APK bu dosyayı Gradle assets olarak paketler. APK ilk açılışta gömülü sayfayı yükler; Render hesabı veya internet bağlantısı yalnızca sayfayı görüntülemek için gerekmez. **Canlı yayınlar için internet gerekir.**

## Önce Android TV'de dene

1. [`apk/Solenz-TV-AndroidTV-debug.apk`](apk/Solenz-TV-AndroidTV-debug.apk) dosyasını TV'ye USB ile taşıyıp "Bilinmeyen uygulamaları yükle" izniyle kur; veya TV'de geliştirici/hata ayıklama etkinse bilgisayardan `adb install -r apk/Solenz-TV-AndroidTV-debug.apk` kullan. TV sürümüne göre `adb pair <TV_IP>:<PAIR_PORT>` ve ardından `adb connect <TV_IP>:<DEBUG_PORT>` gerekebilir. Bilinmeyen APK'ları başka kaynaklardan kurma.
2. TV uygulamaları menüsünden **Solenz TV**'yi aç. Seçili kanal ana ekranda **sessiz önizleme**, "İzle" ile oynatıcıda sesli yayın; kumandada yön tuşları, OK ve geri tuşu kullanılır.
3. Kumandada **MENU/Ayarlar** tuşuyla gömülü sürüm ile daha sonra Render'da yayınlayacağın HTTPS adresi arasında geçiş yapabilirsin. Bazı kumandalarda MENU tuşu bulunmayabilir; uygulama yine varsayılan gömülü sürümle açılır. APK'nın içine giren site değiştiğinde yeni APK derlenip kurulmalıdır; Render adresi seçilirse sayfa güncellemeleri Render'dan gelir.

Bu dosya **debug imzalı test APK'sıdır**, Play Store için üretim sürümü veya kalıcı güncelleme anahtarı değildir. Yeni debug anahtarıyla yeniden imzalanmış sürümler eski sürümün üzerine yüklenmeyebilir. TV modelinde henüz gerçek cihaz testi yapılmadı: Android System WebView, codec desteği, yayıncı CORS kısıtları ve ağ erişimi modelden modele değişir. TV'de WebView kurulu/etkin değilse uygulama bunu bildirir. Kamuya açık yayın listeleri yayın/marka haklarını vermez.

## Render'da siteyi aç (Web Service değil, Static Site)

1. Bu GitHub reposunu Render hesabına bağla.
2. Render'da **New → Blueprint** ile kökteki `render.yaml` dosyasını seç; alternatif olarak **New → Static Site**, depo `kcbyk/solenz_ulusal`, **Publish Directory:** `site`, **Build Command:** `echo prebuilt` gir.
3. Deploy sonrası Render'ın verdiği `https://...onrender.com` adresini TV tarayıcısında aç. İstersen Android TV APK'daki **MENU/Ayarlar → Render / HTTPS adresini ayarla** seçeneğiyle aynı adresi uygulamaya yaz.

**Önemli:** Render hesabı ayrı; GitHub'a kod göndermek Render hizmetini kendiliğinden başlatmaz. Gerçek `onrender.com` adresi hizmeti kurduktan sonra belli olur; bu depoda sahte bir URL yoktur. Render yalnız arayüzü/HTML'yi sunar. Video dosyaları doğrudan yayıncı CDN'lerinden gelir; Render proxy/CDN kısıtlarını aşmaz. Render Static Site üzerinde `source/server.js` ve `/api/*` çalışmaz, bu APK/tek HTML için gerekli değildir. GitHub repo ve Render Static Site herkese açıktır; dağıtım haklarını kontrol edin.

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
