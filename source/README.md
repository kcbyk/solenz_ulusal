# Sinepad · Türkiye Canlı TV

Kullanıcının sağladığı `Sinepad2.html` tasarımı korunarak hazırlanmıştır. Kanal rafı, tür filtreleri, arama, favoriler, kumanda/klavye gezinimi ve tam ekran oynatıcı vardır. **55 kanalın tamamı ve 55 yerel PNG logosu** arayüzdedir. Erişilemeyen yayınlar da listede kalır ama “ŞU AN YOK” olarak işaretlenir; dış siteye yönlendiren düğme yoktur.

## Aç / kullan

- **Tek dosya:** `Sinepad-TV.html` dosyasını tarayıcıda aç. HLS oynatıcı ve logolar gömülüdür. Video için internet gerekir. `file://` kaynaklı medya tarayıcınızda kısıtlanıyorsa aşağıdaki sunucuyu kullanın.
- **Yerel demo:** Node 18+ ile `node server.js`, ardından `http://localhost:3000`. `/classic` eski test arayüzü; `/api/channels` tüm katalog; `/api/playlist.m3u` denetlenmiş oynatılabilir adreslerin M3U listesi. Npm kurulumu gerekmiyor.
- **Kısayollar:** Kategori ikonları, `/` arama, Enter seç, Esc geri, oynatıcıda ↑↓ kanal değiştir, ←→ ses ayarla.

## Kaynakları güncelle

```bash
python3 refresh.py          # IPTV-org ve yayıncı kaynakları ile kanal adreslerini güncelle
python3 audit_channels.py   # yüksek varyant/medya parçası erişimini denetle
python3 build_sinepad.py    # Sinepad-TV.html dosyasını yeniden derle
```

`audit_channels.py` için `requests` gerekir: `python3 -m pip install requests`. Logoları yenilemek için ayrıca `pillow` kurup `python3 prepare_logos.py` çalıştır. Akış ve çözünürlük denetimleri anlıktır; `audit-log.txt` son sunucu denetimi, `browser_audit.json` önceki Chromium taramasını, `adaptive-browser-audit.json` yeni adaptif oynatma taramasını tutar.

## 21 Kasım 2026 testi

- **Show TV, TV8, Kanal D, PowerTürk TV, HT Spor, Power TV:** Chromium'da 1920×1080 video görüntüsü doğrulandı. **TRT 1 ve TRT Haber:** 2560×1440. Yayıncının daha yüksek bir sürüm sunmadığını söylemiyoruz; bu, erişebildiğimiz ve oynatabildiğimiz en yüksek örnektir.
- 55 kayıttan son sunucu taramasında **41'inin medya parçasına erişildi**, 6'sı kontrol edilemedi, 3'ünde manifest olmasına karşın parça alınamadı, 5'inde doğrudan akış bulunmadı. Tarayıcı testinde de medya parçası erişimi oynatma garantisi vermedi. **Star TV, NTV, TJK TV ve VAV TV** bulunan adreslerle Chromium'da oynatılamadığı için arayüzde yayınları devre dışıdır. Sınırlı/çalışmayan başka kanallar da “ŞU AN YOK” gösterilir. `browser_audit.json` sonuçları yalnız bir anlık taramadır; bazen ilk denemede başlayamayan atv, NOW ve A Haber ikinci denemede oynadı.
- **Yeni adaptif başlangıç:** Çoklu kalite sunan **35 yayın** hls.js destekleyen tarayıcılarda en düşük varyantla (çoğunda 360p) açılıyor; hls.js sonra ağ ölçümüne göre otomatik yükseltip gerekirse tekrar düşürüyor. Chromium'da TV8 360p→1080p, Show TV 360p→1080p, TRT 1 360p→1440p gözlendi; 35/35 adaptif yayın ilk görüntüyü verdi (`adaptive-browser-audit.json`). Tek-varyantlı yayın düşük çözünürlükte başlatılamaz. CORS izin vermeyen CDN'lerde önce yerel HLS, o da sorunluysa çalışan doğrudan akış denenir. Ana sayfada seçili kanalın videosu sessiz oynar; kanal değişince önizleme de değişir. Tam ekran oynatıcıdan çıkınca seçili yayının sessiz önizlemesi yeniden başlar. M3U uygulamalarında adaptif kalite davranışı kullanılan uygulamaya bağlıdır.
- “Sitede aç” düğmeleri ve canlı yayında `Infinity:NaN:NaN` üreten süre etiketi kaldırıldı. CDN, ağ kapasitesi, cihaz codec desteği ve yayıncı kısıtları nedeniyle **her kanalda yüksek kalite garantisi verilemez**.

Akış URL'leri her an değişebilir, CORS/coğrafi/DRM kısıtları olabilir; bu proje akışları proxy'lemez veya erişim engellerini aşmaz. [IPTV-org](https://github.com/iptv-org/iptv) listelerinin açık lisansı video ve marka logolarının kullanım hakkı değildir. Yayımlamadan önce yayıncı koşullarını inceleyin. Gömülü [hls.js](https://github.com/video-dev/hls.js) Apache-2.0 lisanslıdır (`vendor/` içinde lisans metni). Logo kaynakları `logo_sources.json` dosyasında; özgün tasarım `Sinepad2-template.html` içinde saklanır.
