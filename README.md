# ÇiftlikPro Enterprise

ÇiftlikPro Enterprise masaüstü ERP kaynak paketi.

## Kaynaktan çalıştırma

Windows'ta `KAYNAKTAN_CALISTIR.bat` dosyasını çalıştırın. Gerekli Python bağımlılıkları `requirements.txt` içindedir.

## Kaynak yapısı

- `app/server.py` — uygulama sunucusu ve arayüz
- `app/desktop_launcher.py` — masaüstü başlatıcı
- `app/feed_catalog.json` — yem kataloğu
- `docs/` — solver referans/doğrulama notları
- `requirements.txt` — Python bağımlılıkları

## Sürüm

Kullanıcı arayüzü: **ÇiftlikPro Enterprise · v3.9.20**

Bu paket GitHub için geliştirme ara paketleri, eski DEV README dosyaları, cache/build/log ve yerel çalışma artıklarından temizlenmiştir.

## GitHub Actions ile Windows kurulum
`.github/workflows/windows-installer.yml` ana branch'e push edildiğinde veya Actions ekranından elle çalıştırıldığında Windows kurulum paketini üretir. Çıktı, workflow çalışmasının **Artifacts** bölümünde `CiftlikPro-Enterprise-V3.9.20-Windows-Setup` adıyla bulunur.
