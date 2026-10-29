# App Edition 2.0.40 doğrulama

26/10/2026 · Yapı: `AppEdition2.0.40-CompactMilkEntry`.

## Python kontrolleri

**157 Python testi geçti.** Manuel laktasyon, mobil referans, hayvan işlemleri, toplu finans gruplama, aktif hayvan raporları, birleşik sağlık merkezi, toplu sağlık / rapel, senkronizasyon, App Edition, arayüz eşitliği, hayvan düzenleme ve metin araması kontrolleri dahil edildi. Seçili PDF / Excel, yem faturası, mükerrer tedavi gideri ve buzağı maliyet testleri de çalıştırıldı. Bu sayı tüm deponun test sayısı değildir.

## Gerçek tarayıcı ve kaydetme

**17 tarayıcı kontrol grubu geçti.** 320, 375, 393, 430, 600, 768, 900, 901, 1024, 1337 ve 1920 pikselde süt girişi denendi. Sabah / Akşam kutuları yan yana kaldı; kapalı ortalamalar içerikleri gizlendi; sayfada yatay taşma olmadı. Kaydetme çubuğunun ekranda ve alt menü / durum çubuğunun üzerinde kaldığı doğrulandı. Mobil ve masaüstü görüntüleri yerel olarak incelendi.

- Test sürüsünde 12 sağmal ve tüm aktif dişiler grubunda 14 hayvan doğru gösterildi. Erkek / satılmış / zayiat kayıtları bu gruba alınmadı. Durumu veya başlangıcı bilinmeyen hayvana sağım günü uydurulmadı.
- Sabah 14,5 ve akşam 13 litre, 27,5 litre olarak hesaplandı. İkinci hayvana 8,25 / 9,75 girildiğinde 18 litre oluştu; liste toplamı 65,5 litre oldu.
- Türkçe karakterli ad, küpe ve eşleşmeyen metin arandı. Aramada gizlenen kartların girişleri korundu; metin temizlenince yüklenmiş grubun tüm kartları geri geldi. Doğrudan arama adresi de temizlenebildi.
- Enter sonraki alana geçti; arama Enter'ı kayıt göndermedi. Liste değiştirme uyarısı iptal edilince yazılmış değerler korundu.
- Gerçek arayüzden yapılan POST yalnız değiştirilmiş iki hayvanın dört süt alanını gönderdi. Günlük kayıtları doğru güncellendi / eklendi. Değiştirilmemiş hayvanın öğle sütü, kalite değerleri ve notları aynı kaldı. Manuel laktasyon ve finans kayıtları değişmedi.
- Mevcut bir günün iki alanını temizleyerek kaydetmek tek sıfır kaydı oluşturdu; kayıt sayısını çoğaltmadı. Negatif giriş tarayıcı doğrulamasını geçmedi. Kaydetme sonrası değişiklik düğmesi tekrar pasif oldu.
- Salt görüntüleme ve arama veritabanını değiştirmedi. JavaScript hatası görülmedi.

Kontroller Chromium ve geçici veritabanında yapıldı. Fiziksel iPhone / Safari ve işletmenin canlı veritabanında test yapılmadı.

## Paket ve çekirdek

220 ana sunucu işlevi / sınıfının kaynak özeti ve mevcut çekirdek doğrulama dosyası 2.0.39 ile aynıdır. Süt ortalama / manuel laktasyon hesapları ve mevcut süt kayıt yolu kullanılır. Yeni veritabanı şeması veya toplu veri dönüşümü eklenmedi.

Python / JavaScript sözdizimi, yeni varlıkların erişimi, önbellek / kurulum sürümü, tam kaynak listesi ve ZIP bütünlüğü kontrol edildi. Paket 2.0.39 tam kaynak dosyalarının tamamını ve dört yeni dosyayı içerir. Test veritabanları, lisanslar, günlükler, önbellekler ve ekran görüntüleri dağıtım paketine alınmaz. Bu ortamda Windows EXE derlenmedi veya kurulu uygulamaya dağıtım yapılmadı.
