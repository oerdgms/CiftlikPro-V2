# 2.0.53 doğrulama — 31.10.2026

- Son birleşik hedefli test koşusu: 70 test, 40,560 saniye, tamamı başarılı. Fotoğraf boyutu/en-boy oranı, asıl dosya bütünlüğü, önizleme tekrar kullanımı ve dosya değişince yenilenmesi, eşzamanlı istekler, yazılamayan önizleme klasörü, geçersiz dosya yolları, bozuk/eski dosya geri dönüşü, HTTP 304 ve 404 davranışları sınandı.
- Mevcut Enterprise kaynak snapshot kontrolü değişmeden geçti. Finans/rasyon hesaplarında ve veritabanı şemasında değişiklik yapılmadı.
- İlk ayrı 49 test koşusunda eski lightbox testinin başlangıç veritabanı hazırlığı eksikti. Geçici veritabanı hazırlanarak son 70 test koşusunda tamamı geçti; ürün koduna bunun için değişiklik yapılmadı.
- Chromium: 320 / 390 / 412 / 820 / 1366 px genişlikte hayvan listesi ve hayvan kartı, toplam 10 görünüm. Görünür fotoğraflar yüklendi; kart fotoğrafı büyütülünce 2200 px asıl dosya açıldı. JavaScript hatası yok.
- Tarayıcıda görünür fotoğrafın ilk isteği bilerek kesildi; cp_retry=1 isteğiyle sayfa yenilenmeden yüklendi. Sürekli hata testinde ilk istek + 2 denemeden sonra istekler durdu.
- Sentetik 2200×1600 JPEG örneği: 3.453.861 bayt asıl dosya, 17.296 bayt 320 px önizleme. Bu örnekte aktarım %99,5 azaldı; gerçek fotoğraflar için aynı oran iddia edilmez.
- 2.0.52 modül hızlandırma testleri ve PWA güncelleme/kurulum testleri kapsamda. Tüm genel test paketi tekrar çalıştırılmadı. Fiziksel iOS/Android veya Windows EXE doğrulaması yapılmadı.
