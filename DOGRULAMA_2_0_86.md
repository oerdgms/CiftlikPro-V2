# AppEdition 2.0.86 — Regresyon uyumu

- Sağlık kartı testi Türkiye saatindeki görünüm ile UTC Windows test verisinin farklı günlerde olmasından etkileniyordu. Test saati sabitlendi; gerçek uygulamanın Türkiye saati korunur.
- Finans testi, buzağı üretim katkısı eklenmeden önceki net açıklamasını bekliyordu. Güncel açıklama kontrol edilir; 65.000 gelir, 45.000 gider, 4.000 maliyet ve 16.000 net kontrolleri korunur.
- Mobil hayvan filtresi testi, taşınmış Kızgınlık kısayolunu arıyordu. Diğer filtrelerdeki seçenek ve seçili durum denetlenir; yetişkin erkek/buzağı ayrımı korunur.
- GitHub Actions test çıktısı ayrıntılıdır (-v); sonraki hatalarda test adı doğrudan görünür.
- 2.0.85 iOS üst başlık düzeltmesi korunur.

Windows EXE üretimi bu ortamda çalıştırılmadı; güncel kaynak paketi GitHub Actions üzerinde derlenmelidir.

Doğrulama: 573 Python regresyon testi geçti. Türkiye/UTC gün farkı senaryosu ayrıca geçti. Python derleme ve sürüm kimliği kontrolleri geçti.
