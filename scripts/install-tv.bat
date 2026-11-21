@echo off
setlocal
set "IP=%~1"
if "%IP%"=="" set "IP=192.168.1.103"
set "TVPORT=%~2"
if "%TVPORT%"=="" set "TVPORT=5555"
set "APK=%~dp0..\apk\Solenz-TV-AndroidTV-debug.apk"
where adb >nul 2>nul
if errorlevel 1 (
  echo ADB bulunamadi. Android SDK Platform Tools kurup adb.exe dosyasini PATH'e ekle.
  exit /b 1
)
if not exist "%APK%" (
  echo APK bulunamadi: %APK%
  exit /b 1
)
echo TV baglantisi: %IP%:%TVPORT%
adb connect %IP%:%TVPORT%
adb devices | findstr /R /C:"^%IP%:%TVPORT%[ ]*device" >nul
if errorlevel 1 (
  echo TV cevrimici degil. Ayni Wi-Fi ve kablosuz hata ayiklama portunu kontrol et.
  echo Android 11+ icin once: adb pair %IP%:^<PAIR_PORT^>
  exit /b 1
)
adb -s %IP%:%TVPORT% install -r "%APK%"
if errorlevel 1 exit /b 1
echo Solenz TV yuklendi. TV uygulama menusunden ac.
