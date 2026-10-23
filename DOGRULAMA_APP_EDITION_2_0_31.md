# App Edition 2.0.31 — Doğrulama

23/10/2026

## Sonuç

- İlgili mevcut regresyon paketinde 200 Python testi geçti: App Edition, mobil üreme, gebelik sonuçları, aşamalar, boş hayvanlar, akıllı yaşam döngüsü, görünüm geçişi, birleşik sağlık ve rapor / kurulum kontrolleri.
- Çekirdek kayıt işleyicileri ve hesap işlevlerinin kaynak özetleri mevcut kayıtla eşleşti. Üreme kayıtları ve hesapları değiştirilmedi.
- 320, 393, 650, 768, 900, 901, 1024 ve 1440 piksel genişliklerde kart yerleşimi kontrol edildi. Kart / sayfa yatay taşması, kimlik–rozet çakışması veya kart dışına çıkan işlem düğmesi görülmedi.
- 393 piksel genişlikte örnek tek işlemli tohumlama kartı önce 290, sonra 156 piksel olarak ölçüldü; yaklaşık %46 küçüldü. Masaüstünde aynı kart 90 piksel. İçeriği ve işlem sayısı farklı kartların yüksekliği değişebilir.
- Kızgınlık, tohumlama, kontrol, gebelik, negatif, belirsiz, boş, doğuma yaklaşan, kuruya çıkarılacak ve yakın doğum görünümleri kontrol edildi. Birden fazla işlemli kartlarda kuruya çıkarma / geri alma düğmeleri korunur.
- Tarayıcıda adın bir bölümüyle arama, padok, aşama, görünüm, akordeon, Tümünü Gör / Daha Az Göster ve klavyeyle hayvan seçimi denendi.
- Sonuç Gir penceresi doğru hayvan ve tohumlama kimliğiyle açıldı. Vazgeç ve gerçek Belirsiz sonucu gönderimi denendi; sonuç geçici test veritabanında doğrulandı.
- Sağlık Yönetimi açıldı; yeni üreme CSS dosyasının başka sayfalara yüklenmediği doğrulandı. Sağlık merkezi kaynakları 2.0.30 ile aynıdır.
- Python sözdizimi kontrolü geçti. Yeni JavaScript veya veritabanı şeması eklenmedi.

## Paket

- Çekirdek sürüm: `3.9.23 DEV4 Hotfix1.22cr`.
- App Edition: `AppEdition2.0.31-CompactReproduction`.
- Mobil kaynak / önbellek kimliği: `2.0.31`.
- Yeni görünüm dosyası: `app/mobile_assets/reproduction.css`. Var olan mobil kaynak klasörüyle Windows paketine dahil edilir.
- Windows çıktı adı: `CiftlikPro_Enterprise_V3_9_23_DEV4_AppEdition_2_0_31_Setup.exe`.
- Kaynak ZIP kullanıcı veritabanı, oturum, lisans, test verisi veya tarayıcı çalışma dosyaları içermez.

Testler geçici veritabanlarında ve yerel Chromium tarayıcısında yapıldı. Windows EXE bu Linux ortamında derlenmedi; kurulum üretimi mevcut GitHub Actions akışını kullanır.
