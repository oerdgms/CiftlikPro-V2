# ÇiftlikPro Enterprise v3.9.20 — Desktop UX Source

Bu kaynak, 6.17 rasyon motorunu **değiştirmeden** ÇiftlikPro'yu klasik web dashboard görünümünden modern masaüstü ERP / rasyon formülasyon yazılımı görünümüne taşır.

## 6.18 Desktop UX
- `pywebview` tabanlı gerçek uygulama penceresi; normal kurulumda tarayıcı adres çubuğu görünmez.
- İnce uygulama başlık çubuğu ve kompakt komut araç çubuğu.
- Sabit/kompakt sol navigasyon ve çalışma sekmesi görünümü.
- Daha sıkı ERP tabloları, küçük köşe yarıçapları ve gölgesiz kartlar.
- Alt durum çubuğu: sistem, veritabanı ve sürüm durumu.
- Mobil görünüm mevcut responsive yapıya geri düşer.

## Rasyon motoru
6.17 besi ve süt solver matematiği değiştirilmeden korunmuştur. Bu sürüm görsel/masaüstü kabuk odaklıdır.

## Çalıştırma
`KAYNAKTAN_CALISTIR.bat` `.venv` oluşturur ve `requirements.txt` bağımlılıklarını kurar. Kurulum paketinde giriş noktası `app/desktop_launcher.py` olmalıdır.
