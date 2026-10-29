# App Edition 2.0.38 doğrulama

26/10/2026 · Yapı: `AppEdition2.0.38-RationPrintReports`.

## Python ve rapor kontrolleri

**105 farklı Python testi geçti:** 98 mevcut App Edition / sağlık / senkronizasyon / arayüz / hayvan düzenleme / arama / kurulum / rapor testi ve 7 yeni hayvan raporu regresyon testi. Yeni testlerin tamamı son çalıştırmada geçti.

- 67 aktif hayvan ve 4 satılmış buzağı bulunan örnekte aktif rapor 67; satılanlar yalnız Satıldı / Tümü seçiminde görünür.
- Aktif raporun hayvan üyeliği Sürü Merkezi ile aynıdır. Yetişkin / buzağı ve dişi / erkek grupları, Türkçe arama, padok, anne küpesi ve geliş tarihi korunur.
- Yetişkine aktarılmış buzağı mükerrer sayılmaz. Zayiat kaydı olan eski Aktif işaretli hayvanlar aktif rapora katılmaz.
- Satıldı / Kesildi / Tümü filtrelerinde gerçek buzağı durumları korunur. Boş / NULL durumların mevcut Aktif varsayımı sürer.
- HTTP ekranı, yazdırma önizlemesi, doğrudan PDF ve Excel dosyalarında aktif / satılan seçiminin aynı olduğu doğrulandı.
- Rapor oluşturmak hayvan, buzağı, finans veya zayiat kayıtlarını değiştirmez.

## Tarayıcı kontrolleri

**13 tarayıcı kontrol grubu geçti.** Masaüstünde 901, 1024, 1337, 1440 ve 1920 piksel genişliklerinde Rasyonu Yazdır düğmesi görünür, başlık alanına sığar ve seçili reçetenin hazırlama raporunu açar. 67 hayvan × 7 gün için toplam yem ve maliyet kontrol edildi; Yazdır / PDF düğmesi tarayıcının yazdırma çağrısını çalıştırdı. Yazdırma görünümünde kontrol düğmeleri gizlendi, rapor tablosu görünür kaldı.

Kaydedilmemiş yem değişikliğinin rapora otomatik kaydedilmediği, mevcut süt rasyonu hazırlama raporunun doğrudan açıldığı ve rasyon listesinde seçimsiz bir yazdırma bağlantısı oluşmadığı denendi. Süt rasyonunun çalışma masası bu kontrolün kapsamına alınmadı.

393, 768 ve 900 piksel mobil görünümde masaüstüne özel yeni düğme gizlidir ve sayfa yatay taşmaz. 393 ve 1440 pikselde 67 aktif / 4 satılan / 71 tüm hayvan filtreleri ve dışa aktarım bağlantılarındaki durum filtresi denendi. JavaScript hatası görülmedi. Masaüstü ve mobil rapor ekran görüntüleri yerel olarak incelendi.

Kontroller Chromium ve geçici test veritabanında yapıldı. Fiziksel iPhone / Safari veya fiziksel yazıcı üzerinde test yapılmadı.

## Paket ve çekirdek

2.0.37 kaynak paketi korunarak yeni rapor modülü, rapor testleri ve 2.0.38 notları eklendi. 220 ana sunucu işlevi / sınıfının kaynak özeti ve mevcut çekirdek doğrulama dosyası değişmedi. Rapor seçim işlevi App Edition kurulumu sırasında ortak rapor modülüne bağlanır; mevcut ekran / PDF / Excel işleyicileri bu seçimi kullanır. Çözücü hesapları ve veritabanı şeması değişmedi.

Python / JavaScript sözdizimi, Windows paketindeki yeni modül, kurulum / önbellek sürüm eşleşmesi ve ZIP bütünlüğü kontrol edildi. Test veritabanları, lisanslar, önbellekler, günlükler ve ekran görüntüleri pakete eklenmez. Bu ortamda Windows EXE derlenmedi veya kurulu uygulamaya dağıtılmadı.
