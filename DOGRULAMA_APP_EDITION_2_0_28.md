# App Edition 2.0.28 — Doğrulama

Tarih: 22/10/2026. Başlangıç paketi: App Edition 2.0.27 Durum Ekle Penceresi FULL; 2.0.26 üzerinde yapılan senkronizasyon çalışması bu sürümle birleştirildi.

## Sonuçlar

- Python regresyonu: 412 test, tamamı başarılı (381 saniye). Yeni senkronizasyon modülünün 13 entegrasyon testi ve önceki Durum Ekle / Doğum Ekle penceresinin 5 testi bu sayıya dahildir.
- Yeni modül ve değişen Python kaynakları derleme / sözdizimi kontrolünden geçti.
- synchronization.js sözdizimi kontrolü başarılı.
- Mevcut sağlık ajandası JavaScript testi başarılı.
- Mevcut rasyon taslak / kilit koruma JavaScript testi başarılı.
- Çevrimdışı DOM testi başarılı: başlangıçtan hesaplanan tarihler, gece yarısı ve ay geçişi, düve / inek takvim filtreleri, toplu seçim, boş doz alanları, değiştirilmiş takvimi koruma, ücret önizlemesi ve gönderilen adımlar.

## Yeni entegrasyon testlerinin kapsamı

- Plan kaydı sağlık uygulaması veya finans gideri oluşturmaz; aynı istek tekrarlandığında plan çoğalmaz.
- Erkek, gebe, sonuç bekleyen, satılmış / kayıp ve başka aktif planı bulunan hayvanlarda toplu işlem atomik reddedilir.
- Doğum sonrası gün hesabı, elle belirlenmiş Düve durumu ve doğum geçmişi bilinmeyen dişilerin ayrımı doğrulandı.
- Her hayvan için ayrı, saatli görev ve doğru plan / hayvan / adım bağlantısı oluşturulur.
- Gerçek uygulama saati kaydedilir; sonraki adım kaymaz; tekrarlanan istek ikinci sağlık kaydı açmaz.
- Gelecek tarih, sıra atlama, geçersiz dozlar ve eksik uygulama bilgileri engellenir.
- Finans kaydı açık işlemle her hayvana ayrı eklenir; kuruş hesabı ve mükerrer gider koruması doğrulandı.
- Hayvan bazında iptal, sonradan oluşan gebelikte hormon görevinin gizlenmesi ve uygulama engeli doğrulandı.
- Plan / adım düzenleme, eski formdan değişiklik ezme koruması, silme ve yeniden başlatma sonrası kalıcılık doğrulandı.
- Tohumlama açık işlemle kaydedilir veya aynı günkü kayda bağlanır.
- HTTP oturum, lisans, form tokenı, HTML kaçışları ve yeni statik dosyaların sunulması doğrulandı.
- Modüller ekranının 15 kutucuğu ve sürüm / kurulum adlarının uyumu kontrol edildi.

Çekirdeğin kayıt ve rasyon hesaplama koruma testleri geçti. Koruma testi yalnız eklenen iki satırlık senkronizasyon dashboard bağlantısını ayırarak aynı özgün kaynak özetlerini denetlemeyi sürdürür; eski hesaplama özetleri yeniden yazılmadı.

## Doğrulama sınırları

Gerçek iPhone / Android ve masaüstü tarayıcıda piksel / kaydırma kontrolü tamamlanamadı. Bulut tarayıcısıyla yerel önizlemeyi açma işlemi, uygulama içeriğinin dış hizmete aktarılma riski gerekçesiyle otomatik onay incelemesinde reddedildi. Çevrimdışı DOM testleri tarayıcı görüntüsü veya cihaz testi yerine geçmez.

Windows EXE bu Linux ortamında derlenmedi / kurulmadı. GitHub Actions derleme tanımı, yeni modülün PyInstaller eklemesi, statik dosya denetimleri ve 2.0.28 kurulum adı güncellendi. ZIP hazır EXE içermez.

## Kurulum sonrası kısa kontrol

1. Modüller → Senkronizasyon → Senkronizasyon Tanımla ekranını açın.
2. Veterinerin belirlediği takvimle uygun hayvanları seçip saatleri inceleyin; Doğum sonrası / Düve / Boş filtrelerini kontrol edin.
3. Oluşan görevden ilgili hayvanın adımına gidildiğini ve aynı planın telefon ile bilgisayarda göründüğünü doğrulayın.
4. Uygulamayı gerçek gerçekleşen zamanda kaydedin; ücretleri yalnız gerçek gideri kaydetmek istediğinizde finansa işleyin.
