# MobileAPI14 Doğrulama

- Python `py_compile`: geçti.
- Mobile web gömülü JavaScript `node --check`: geçti.
- API14 statik kapsam kontrolleri: 8/8 geçti.
- Temiz geçici veritabanında şema/migrasyon kontrolü: animal_losses genişletilmiş maliyet alanları ve finance.calf_id mevcut.
- Eski mobil test paketinin 26 testi çalıştırıldı; 22 geçti, 4 test yalnız eski `MOBILE_API_BUILD='MobileAPI11-DesktopDailyOps'` sabitini beklediği için sürüm etiketi uyuşmazlığı verdi. Bu eski beklenti API14 build etiketi nedeniyle bilinçli olarak geçersizdir.
