# App Edition 2.0.29 — Doğrulama

22/10/2026. Mobil hayvan listesindeki tekrarlanan laktasyon bandının kaldırılması.

- İlgili App Edition, mobil referans, hayvan işlemleri senkronizasyon ve mobil/masaüstü bütünlük testleri: 72 başarılı.
- Chromium / Playwright, ayrı deneme veritabanı: 390 ve 768 pikselde Tümü, Sağmal, Kuru, Düve, Gebe ve Kızgın; toplam 12 filtre görünümü kontrol edildi. Bant hiçbirinde bulunmuyor; filtre sayıları doğru ve yatay taşma yok.
- Canlı filtre değişimi, arama, boş sonuç ve tarayıcı geri dönüşünden sonra bant yeniden eklenmedi.
- Her iki genişlikte hayvan kartındaki Durum Ekle açıldı. Sağmal, Kuru ve Düve seçimlerinin doğru hayvan kimliğini ve doğru durum değerini taşıyan formları açtığı doğrulandı.
- 1322 pikselde masaüstü liste/satır durum işlemleri görünür; eski liste yedek kısayolu yok. Süt & Laktasyon bölümündeki toplu durum erişimi kullanılabilir.
- JavaScript sayfa hatası: 0. Düve listesi 390 pikselde gözle incelendi.
- Önceki paketle kaynak karşılaştırmasında app/server.py içinde yalnız yapı kimliği değiştiği doğrulandı.

Tam regresyon bu küçük görünüm değişikliği için yeniden çalıştırılmadı; ilgili testler tekrarlandı. Gerçek iPhone/Safari ve Windows EXE üzerinde test yapılmadı. Tam kaynak ZIP'i işletme/deneme verisi, QA betikleri veya Python önbelleği içermez.

Sürüm uzlaştırması: en güncel 2.0.28 Senkronizasyon tam kaynak paketi temel alındı. Liste bandı düzeltmesi bu çalışma kopyasına yeniden uygulandı. Senkronizasyon Python/CSS/JavaScript dosyaları, testleri, masaüstü modül ekranı, paket tanımı ve 2.0.28 notları önceki paketle birebir aynı kaldı. 2.0.29 sürüm kimliği ve liste görünümü dışında işlev değişikliği yapılmadı.
