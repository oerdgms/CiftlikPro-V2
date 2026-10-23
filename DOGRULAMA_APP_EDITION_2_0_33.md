# App Edition 2.0.33 — Doğrulama

23/10/2026

**2.0.33a ek doğrulama:** Eski ana sayfa kısayolu beklentisi güncellendikten sonra GitHub ile aynı discovery komutunda 434 testin tamamı geçti. Uygulama / kurulum / workflow kaynakları 2.0.33 ile birebir aynıdır. Ayrıntılar: DUZELTME_NOTLARI_2_0_33a.md.

## Kontroller

- App Edition, sürüm / kurulum / kaynak bütünlüğü, mobil referans verileri, birleşik sağlık, rapor / içe aktarma, mobil üreme ve yeni metin arama paketlerinde 195 Python testi geçti.
- Türkçe / düz klavye eşleşmesi, kısmi küpe numarası, birden fazla kelime, boş sorgu, eşleşmeyen sorgu ve parametreli SQLite araması kontrol edildi. SQL araması veri değiştirmedi.
- 35 kayıt arkasındaki hedefin bulunması ve aramanın durum / tür / padok filtreleriyle sayfalamadan önce çalışması otomatik testle doğrulandı.
- Geçici veritabanı ve Chromium ile 393 ve 1440 piksel genişliklerde hayvan, finans, süt, sağlık, yem kataloğu, satılan arşivi, üreme ve padok aramaları gerçek yazma / tıklamalarla denendi.
- Hayvan aramasında ilk sayfada bulunmayan kayıt, isim, küpe, padok, not, Türkçe karakter, boş sonuç, temizleme, hızlı sorgu değişimi, metin birleştirme, odak ve mobil/masaüstü filtre eşleşmesi kontrol edildi.
- Sağlık seçim listesinde arama değişince seçili hayvanın korunması doğrulandı. Tarayıcıda JavaScript sayfa hatası görülmedi.
- “Ana Sayfayı Düzenle” düğmesi 901, 1024, 1337, 1440 ve 1920 piksel masaüstü genişliklerinde kontrol edildi; düğme mevcut düzenleyiciyi açtı.
- Kayıt yazan App.do_POST kaynak kodu 2.0.32 ile birebir aynıdır. Sağlık kategori kuralları, üreme hesapları ve veritabanı şeması değiştirilmedi.

## Paket

- Çekirdek: `3.9.23 DEV4 Hotfix1.22cr`.
- App Edition: `AppEdition2.0.33-LiveTextSearch`.
- Kaynak / önbellek kimliği: `2.0.33`.
- Windows çıktı adı: `CiftlikPro_Enterprise_V3_9_23_DEV4_AppEdition_2_0_33_Setup.exe`.
- Yeni `app/text_search.py` ve `app/mobile_assets/search.js` tam kaynak paketine ve Windows paketleme tanımına dahil edildi.

Kontroller geçici veritabanları ve yerel Chromium üzerinde yapıldı. Windows EXE Linux ortamında derlenmedi; mevcut GitHub Actions akışı üzerinden oluşturulur. Paket kullanıcı veritabanı, lisans, oturum, tarayıcı görüntüsü veya önizleme verisi içermez.
