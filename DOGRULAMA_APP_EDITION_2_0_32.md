# App Edition 2.0.32 — Doğrulama

23/10/2026

## Kontroller

- İlgili mevcut paketlerde 52 Python testi geçti: App Edition, kaynak / sürüm / kurulum, çekirdek kaynak özeti, mobil referans verileri, dashboard verileri / önbelleği ve önceki masaüstü düzeni.
- 901, 1024, 1337, 1440 ve 1920 piksel masaüstü genişliklerinde gerçek sayfa kontrol edildi. Karşılama → toplam kartları → Sürü Özeti → iş panelleri sırası doğrulandı.
- Ayar düğmesinin içerik alanının ortasında olduğu ve başlık / sağ kontrollerle çakışmadığı ölçüldü. Modüller rozeti üst menüye sığdı; sayfa ve kart bölümlerinde yatay taşma görülmedi.
- Aylık Net, örnekteki 193.063,62 TL tutarıyla kontrol edildi. Sayının tek satırda kalması ve dar masaüstünde taşmaması doğrulandı.
- Modüller → modül dizini → Sağlık Yönetimi gerçek tıklamalarla açıldı. Kişisel hızlı menü seçimi ve sıfırlaması sırasında rozet görünür kaldı. Eski modül adresi de kontrol edildi.
- Ayar düğmesi klavyeyle açıldı; bir sürü kartını kaldırma, kaydetme ve varsayılana dönme gerçek formlarla denendi. Kart seçimi hem masaüstü hem mobil veri kaynağıyla aynı kaldı.
- Modern / Klasik geçişleri, Klasikte toplamların ardından Sürü Özeti ve mevcut masaüstü kart düzenleyicisi kontrol edildi. İç içe kart yapısı bozulmadı.
- 393, 768 ve 900 piksel mobil görünümde mevcut ana sayfa gösterildi; yeni masaüstü kontrolleri gizli kaldı ve yatay taşma görülmedi.
- Kompakt üreme kartları ve Sonuç Gir penceresi kontrol edildi. Birleşik sağlık, senkronizasyon, üreme CSS'i, mobil referans verileri ve kişisel düzen kaydı kaynakları 2.0.31 ile aynıdır.
- JavaScript sayfa hatası görülmedi. Yeni JavaScript veya veritabanı şeması eklenmedi.

## Paket

- Çekirdek: `3.9.23 DEV4 Hotfix1.22cr`.
- App Edition: `AppEdition2.0.32-DesktopHome`.
- Kaynak / önbellek kimliği: `2.0.32`.
- Windows çıktı adı: `CiftlikPro_Enterprise_V3_9_23_DEV4_AppEdition_2_0_32_Setup.exe`.
- ZIP tam kaynak paketidir; kullanıcı veritabanı, lisans, oturum veya önizleme verisi içermez.

Kontroller geçici veritabanlarında ve yerel Chromium tarayıcısında yapıldı. Windows EXE bu Linux ortamında derlenmedi; mevcut GitHub Actions akışı üzerinden oluşturulur.
