# AppEdition 2.0.53 — Küçük fotoğraf önizlemeleri

2.0.52 üzerine hazırlanmıştır. Kaynaktan çalıştırma paketi; EXE içermez.

- Hayvan listelerinde 320 px, kart ve galeri önizlemelerinde 640 px üst sınır kullanılır. En-boy oranı ve EXIF yönü korunur.
- Fotoğrafa dokununca kayıtlı asıl dosya açılır. Asıl fotoğraflar ve veritabanı değiştirilmez.
- Önizlemeler gerektiğinde üretilir ve sunucudaki uploads/.photo-previews içinde tekrar kullanılır. Asıl dosya değişirse önizleme yenilenir. Aynı fotoğrafın eski önizleme sürümleri birikmez.
- Tarayıcı özel önbelleği ETag ile doğrulanır; değişmeyen önizleme yeniden aktarılmaz. Fotoğraflar PWA çevrimdışı önbelleğine eklenmez.
- Geçici fotoğraf hatasında en fazla iki otomatik yeniden deneme yapılır; son denemede asıl dosya da denenebilir. Sayfa yeniden yüklenmez.
- Eski biçimde önizleme üretilemiyorsa asıl dosyaya dönülür. Eksik dosya yanıtları önbelleğe alınmaz. Önizleme klasörüne yazılamıyorsa bellekte üretilir.

## Kullanım

Bilgisayardaki uygulamayı kapatıp bu sürümü mevcut veri konumuyla kaynaktan çalıştırın. Telefondaki Uygulama ve güncellemeler bölümünden Güncellemeyi kontrol et ve yeni sürümü yükleme/yenileme işlemini kullanın. Uygulama simgesini yeniden kurmanız gerekmez. Telefon düğmesi bilgisayardaki kaynak paketini kendisi kurmaz.

İlk fotoğraf açılışında önizleme bir defa hazırlanır. Sonraki açılışlarda hazır kopya kullanılır. Gerçek telefondaki hız bağlantıya ve fotoğraflara bağlıdır.
