# AppEdition 2.0.47 Doğrulama

Tam regresyon: 499 test, 279,664 saniye, OK. Yedi yeni yeniden hesaplama testi dahildir.

Kapsam: önizlemede rasyonun değişmemesi; aynı rasyon kimliği, adı ve padok bağlantısının korunması; kilitli miktarlar ve kilitlerin korunması; önceki günlerin miktar geçmişinin değişmemesi; güncel olmayan önizlemeyi reddetme; yem analizi/fiyat/kalem değişikliklerini algılama; kullanıcı kapsamı, 20 dakika süre ve tek uygulama; başarısız çözümde mevcut kaydı koruma; geçersiz ağırlık ve süt rasyonunu reddetme; HTTP önizleme/uygulama akışı ve giriş kontrolü. Gerçek solver testi 1,234 kg kilitli miktarın yuvarlanmadan korunmasını ve güncel sınır dışındaki kilidin reddedilmesini doğrular.

Chromium 320/390/412/1366 pikselde gerçek solverle 12 önizleme, vazgeçme ve uygulama kontrolü geçti. 450 kg ve %2,50 ile 11,25 kg KM hedefi gösterildi. Vazgeçince kalemler değişmedi, uygulayınca aynı rasyon kimliğine dönüldü. Önizleme tablosunda yatay taşma ve JavaScript hatası gözlenmedi.

Sürüm eşleme, Python kaynak ayrıştırma ve JavaScript sözdizimi kontrolü geçti. Mevcut kaynak özeti yalnız App, init_db ve solve_smart_ration tanımları için yetkili değişikliklere göre güncellendi. Önceki diğer çekirdek karşılaştırmalar korundu. Yeni ration_recalculation modülü Windows kaynak paketine eklendi.

Geçici veritabanları kullanıldı; kullanıcının işletme verilerine erişilmedi. Fiziksel iPhone/Android kontrolü ve Windows EXE derlemesi yapılmadı. Tam kaynak paketi sağlandı.
