# App Edition 2.0.36 doğrulama

24/10/2026 · Yapı: `AppEdition2.0.36-ReproductionSync`.

## Kontroller

İlgili **83 Python regresyon testi geçti**: App Edition, arayüz eşitliği, birleşik sağlık, hayvan düzenleme, metin araması ve senkronizasyon. Mevcut HTTP testi; yeni düğmenin tohumlamadan sonra gelmesini, eski üst kısayolların bulunmamasını, ayrı senkronizasyon ekranını ve Sağlık Yönetimi’nin aynı planı göstermesini de doğrular.

**12 tarayıcı kontrol grubu geçti**:

- 320, 393, 600, 900, 1024, 1337, 1440 ve 1920 piksel genişliklerinde Üreme Yönetimi düğmesi → senkronizasyon listesi → tanımlama penceresi → Üreme Yönetimi’ne dönüş.
- Aktif, Tamamlanan, İptal ve Tümü filtreleri.
- Mobil formdan yeni planın gerçek POST ile kaydedilmesi ve ayrıntısının açılması.
- Yeni kaydın hem ayrı senkronizasyon listesinde hem Sağlık Yönetimi → Senkronizasyon’da görülmesi.
- Mevcut doğrudan yeni kayıt bağlantısının formu açması.

Tarayıcı denemeleri Chromium üzerinde, geçici test veritabanıyla yapıldı. JavaScript hatası görülmedi. Sayfa ve tanımlama penceresi yatay olarak ekran dışına taşmadı. Masaüstü / mobil düğme yerleşimi ve mobil liste ekran görüntüleri yerel olarak incelendi. Fiziksel iPhone / Safari testi yapılmadı.

## Kapsam

Temel 2.0.35 tam pakettir. Ana sunucudaki kayıt işleyicileri ve hesaplama işlevleri değiştirilmedi; Enterprise kaynak özeti denetimi geçti. Senkronizasyonun plan oluşturma, uygulama, iptal, maliyet, sağlık kaydı ve idempotent kayıt işlevleri korunur.

Değişiklikler, üreme işlem çubuğundaki giriş, ayrı senkronizasyon ekranına GET yönlendirmesi, geri dönüş bağlantısı ve sürüm etiketleridir. Sağlık Yönetimi’nin senkronizasyon sekmesi aynı işlevleri ve verileri kullanır. Veritabanı şeması değiştirilmedi.

Python sözdizimi ve ZIP bütünlüğü kontrol edildi. Önceki paketin tüm dosyaları korunur; 2.0.36 değişiklik / doğrulama notları eklenir. Test veritabanları, kişisel lisanslar ve tarayıcı ekran görüntüleri dağıtım paketine dahil edilmez.

Bu ortamda Windows EXE üretilmedi veya kullanıcının kurulu uygulamasına dağıtım yapılmadı. Windows kurulumu ZIP içindeki GitHub Actions iş akışıyla oluşturulur.
