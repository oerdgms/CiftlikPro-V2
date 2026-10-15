# MobileAPI17 doğrulama

- `python -m py_compile app/server.py`: geçti.
- Mobile web JavaScript, `App.mobile_app_html()` içinden çıkarılıp `node --check` ile doğrulandı: geçti.
- `tests.test_photo_lightbox`: 2/2 geçti.
- `tests.test_mobile_animal_actions`: işlev testi eski sürüm numarasını (`1.22ci`) sabit beklediği için yalnız sürüm assertion'ında kaldı; API17 davranışıyla ilgili bir hata değildir.
- Fotoğraf detay endpoint'lerinde yetişkin ve buzağı için son `animal_photos/calf_photos` kaydı profil fotoğrafı olarak kullanılıyor.
- `photoForm` tek-instance koruması içeriyor.
