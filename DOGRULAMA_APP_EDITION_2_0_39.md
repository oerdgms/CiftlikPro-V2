# App Edition 2.0.39 doğrulama

26/10/2026 · Yapı: `AppEdition2.0.39-GroupedHealthFinance`.

## Python kontrolleri

**125 Python testi geçti.** Bunların 14'ü yeni finans gruplama testidir. Sağlık ve toplu uygulama, raporlar, senkronizasyon, App Edition, arayüz eşitliği, hayvan düzenleme, arama, buzağı satışı, finans / fatura dönüşümü ve maliyet kontrolleri dahil edildi.

- 67 mevcut sağlık gideri tek görünür işlem ve 6.700 TL toplam olarak gösterildi. 67 sağlık / gider kaydı korunur; listeleme veriyi değiştirmez.
- Aynı ad / tarihli ayrı programlar ve serbest giderler birleşmez. Farklı dozlar ve ödeme koşulları ayrı tutulur.
- Gruplama sayfalamadan önce uygulanır; eski sayfa numarası yeni işlem sayısına göre sınırlandırılır.
- Küpe / işlem araması, tarih, kategori, tür ve ödeme durumu filtreleri doğru eşleşen tutarı gösterir.
- Hayvan başına tutar düzenlemesi kuruş hassasiyetiyle grup toplamına yansır. Uygulamayı geri alma ve yinelenen tamamlama gideri çoğaltmaz.
- Eski çoklu programlar, parazit / vitamin / tedavi programları ve hastalık gider dağılımı denendi. Çakışan sağlık bağlantıları toplamı mükerrer saymaz.
- Ayrıntı bütün 67 hayvanı açar; metin kaçışı, güvenli dönüş adresi, oturum kontrolü ve eşzamanlı farklı filtre istekleri doğrulandı.
- Yem faturası önizleme / ödeme ve normal düzenleme / silme bağlantıları korundu.

## Tarayıcı kontrolleri

**14 tarayıcı kontrol grubu geçti.** 320, 375, 393, 430, 600, 768, 900, 901, 1024, 1337 ve 1920 pikselde 67 hayvanlık gider tek satırda gösterildi. Her genişlikte tüm dağılım açıldı; Türkçe ad, eski sayfa sınırının dışındaki küpe ve eşleşmeyen metin arandı. Toplam sabit kaldı; dönüşte kategori korundu. Yatay taşma görülmedi ve salt görüntülemede finans / sağlık kayıtları değişmedi.

Normal gider / gelirlerin ve yem faturası önizlemesinin toplu görünümle birlikte çalıştığı denendi. Ana Finans canlı araması bir küpe için tek gideri buldu; arama temizlenince grup geri geldi. Ayrıntıdan gerçek sağlık düzenleme formu açılarak bir hayvanın 100 TL gideri 200 TL yapıldı. Grup 6.800 TL'ye çıktı; hayvan ve finans tutarları eşitlendi, mevcut dönemin 67 rapeli beklemede kaldı.

JavaScript hatası görülmedi. Mobil ve masaüstü liste / ayrıntı görüntüleri yerel olarak incelendi. Kontroller Chromium ve geçici test veritabanında yapıldı; fiziksel iPhone / Safari veya kullanıcı işletmesinin canlı veritabanında test yapılmadı.

## Paket ve çekirdek

Yeni görünüm yalnız finans kayıtlarını okur ve program / görev / hastalık bağlantılarıyla gruplar. 220 ana sunucu işlevi / sınıfının kaynak özeti, çekirdek doğrulama dosyası ve veritabanı şeması değişmedi. Mevcut finans giriş formları, sağlık kayıt işlemleri ve rapor / maliyet hesapları kullanılır. İstek filtreleri iş parçacıkları arasında paylaşılmaz.

Yeni modül Windows paketine eklenir; varlık yolları, önbellek / kurulum sürümü, Python / JavaScript sözdizimi ve ZIP bütünlüğü kontrol edildi. 2.0.38 tam kaynak paketi ve önceki düzeltmeler korunur. Test veritabanları, lisanslar, günlükler, önbellekler ve ekran görüntüleri dağıtım paketine alınmaz. Bu ortamda Windows EXE derlenmedi veya kurulu uygulamaya dağıtım yapılmadı.
