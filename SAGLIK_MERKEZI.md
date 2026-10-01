# Hotfix1.22ai - Sağlık Merkezi ve yaklaşan işler

- Ana sayfadaki bekleyen işler artık eski planları, yeni doz/tedavi görevlerini ve önümüzdeki 30 günün gebelik aşılarını birlikte gösterir. İlk dört sağlık satırı sınırı kaldırıldı; liste kendi içinde kayar.
- Bugün Yapılacak göstergesi yalnız bugün tarihli işleri sayar.
- Sağlık kartları tarih kutusu, durum rozeti ve daha kompakt işlem düğmeleriyle yeniden düzenlendi; planlar tarih sırasıyla gösterilir.
- PDF indir / Yazdır ana sayfadan Sağlık ekranına taşındı. Çıktı seçili filtre ve küpe/ürün/işlem aramasını takip eder; yalnız bekleyen sağlık işlerini içerir. Hayvan Dosyaları geçmiş ekranında çıktı düğmeleri gizlidir.
- Padok uygulamaları çıktıdaki tek satırda hayvan sayısıyla özetlenir. Gebelik aşıları 30 günlük pencereyle alınır.
- Rasyon taslak koruması korunur. Solver, bilimsel eşikler ve stok tüketimi değiştirilmedi.

Kontrol: mevcut 137 Python testi ve ek sağlık entegrasyon testi geçti. Rasyon taslak betiği testleri tekrar geçti. Çok sayfalı A4 PDF görsel olarak kontrol edildi. Tarayıcı yerleşimi ve kullanıcının kendi kayıtlarıyla kurulum testi henüz doğrulanmadı.

