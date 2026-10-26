# App Edition 2.0.37 doğrulama

24/10/2026 · Yapı: `AppEdition2.0.37-BulkHealth`.

## İşlev ve veri kontrolleri

**93 Python testi geçti.** App Edition, kaynak özeti / arayüz eşitliği, sağlık, senkronizasyon, hayvan düzenleme, metin araması ve eski çoklu plan bağlantıları kontrol edildi. Toplu işlem için eklenen / genişletilen kontroller:

- 67 hayvanın ilk dozunu aynı gönderimde tamamlama; ayrı sağlık / finans kayıtları ve toplam 827,45 TL maliyet.
- Gerçek uygulamaya göre rapel ve sonraki dönem tarihi; rapelin yapılmış sayılmaması.
- Aynı gönderimin tekrarı ve yinelenen görev kimlikleriyle ikinci kayıt oluşmaması.
- Kısmi seçim, padok değişimi ve programa sonradan eklenmemiş hayvanların seçime katılmaması.
- Eksik / bozuk / karışık görev, değişmiş tarih, gelecek gerçek tarih ve pasif hayvanda tüm işlemin geri alınması.
- Önceki dozu veya gün içindeki önceki uygulaması yapılmadan sonraki aşamanın kaydedilememesi.
- Eski çoklu aşı programında sonraki dozun gerçek tarihten hesaplanması.
- Parazit, vitamin / mineral ve duraklatılmış program kontrolleri.
- 25 satırlık sayfada 67 hayvanlık önizleme; HTML / JSON metin kaçışı.
- HTTP oturum / CSRF denetimi ve yinelenen POST.

## Tarayıcı kontrolleri

**16 tarayıcı kontrol grubu geçti.** 320, 375, 393, 430, 600, 768, 900, 1024, 1337 ve 1920 piksel genişliklerinde 67 hayvanlık toplu seçim penceresi, sınırlar ve vazgeçme denendi. Arama / padok, yalnız görünenleri seç, tümünü seç, temizle, seçimden çıkarma ve toplam maliyet kontrol edildi. Arama kutusunda Enter kayıt göndermedi.

Mobil tarayıcı formundan 67 ilk doz gerçek POST ile bir kez kaydedildi. Aynı POST tekrarlanarak sağlık / gider sayılarının değişmediği doğrulandı. Eski 67 hayvanlık programda bir hayvan dışarıda bırakılarak 66 kayıt oluşturuldu; kalan hayvan beklemede kaldı. Parazit, vitamin / mineral ve tedavi programlarında pencere açıldı. Ana sayfanın kısa özetinden doğru program / doz grubuna giriş denendi.

JavaScript hatası görülmedi. Mobil ve masaüstü ekran görüntüleri yerel olarak incelendi. Seçilen sayı ve maliyet alt bölümde görünür kalır. Denemeler Chromium ve geçici test veritabanında yapıldı; fiziksel iPhone / Safari üzerinde test yapılmadı.

## Paket

2.0.36 dosyaları korunur; 2.0.37 değişiklik ve doğrulama notları eklenir. Ana sunucu işleyicileri / çözücü kaynak özeti ve veritabanı şeması korunur. Toplu kayıt, mevcut sağlık kayıt işlevi üzerinden tek veritabanı işlemi içinde çalışır. Eski aşı programlarının sonraki bekleyen doz tarihleri için uyumluluk eklendi.

Python / JavaScript sözdizimi ve ZIP bütünlüğü kontrol edildi. Test veritabanları, lisanslar ve tarayıcı ekran görüntüleri dağıtım paketine eklenmez. Bu ortamda Windows EXE derlenmedi veya kurulu uygulamaya dağıtım yapılmadı; kurulum GitHub Actions ile oluşturulur.
