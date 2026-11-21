#!/usr/bin/env bash
# Run on a computer on the same home network as your Android TV.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IP="${1:-192.168.1.103}"
PORT="${2:-5555}"
ADB="${ADB:-adb}"
APK="$ROOT/apk/Solenz-TV-AndroidTV-debug.apk"
if ! command -v "$ADB" >/dev/null 2>&1; then
  echo "ADB bulunamadı. Android SDK Platform Tools kur veya ADB değişkenini adb yoluna ayarla." >&2
  exit 1
fi
if [[ ! -f "$APK" ]]; then echo "APK bulunamadı: $APK" >&2; exit 1; fi
echo "TV'ye bağlanılıyor: $IP:$PORT"
"$ADB" connect "$IP:$PORT"
if ! "$ADB" devices | grep -q "^$IP:$PORT[[:space:]]*device$"; then
  echo "TV çevrimiçi değil. Aynı Wi-Fi, TV geliştirici seçenekleri ve kablosuz hata ayıklama portunu kontrol et." >&2
  echo "Android 11+ eşleştirme için önce: adb pair $IP:<PAIR_PORT>" >&2
  exit 1
fi
"$ADB" -s "$IP:$PORT" install -r "$APK"
echo "Tamam: Solenz TV yüklendi. Televizyonun uygulama menüsünden aç."
