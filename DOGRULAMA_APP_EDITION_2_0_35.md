# App Edition 2.0.35 doğrulama

24/10/2026 · Yapı: `AppEdition2.0.35-ResponsiveHerd`.

## Otomatik kontroller

- İlgili 70 Python regresyon testi geçti: App Edition, arayüz eşitliği, birleşik sağlık, hayvan düzenleme ve canlı metin araması.
- 19 mobil tarayıcı kontrolü geçti. 320, 375, 393, 430, 600, 768 ve 900 piksel genişliklerinde sağlık formları ve yetişkin / buzağı düzenleme panelleri kontrol edildi. Senkronizasyon, padok, rasyon, yem ve finans pencereleri de incelendi.
- 6 masaüstü tarayıcı kontrolü geçti. 1024, 1180, 1337, 1440 ve 1920 pikselde Ayrıntı / Kart / Kompakt görünümleri ve sayfa genişliği kontrol edildi. 67 hayvan içinden ilk sayfada bulunmayan bir kayda canlı aramayla ulaşıldı; sıralama ve kayıt sayısı seçimi korundu.

Telefon düzeninde tarih ve maliyetin ayrı tam satırlarda olduğu, `125,50` tutarının değişmediği, form kontrollerinin pencere sınırlarını aşmadığı doğrulandı. Düzenleme alanının dikey kayması çalışır; yatay tekerlek hareketi veya kaydırma konumu verilmesi içeriği yana taşımaz. Uzun fotoğraf dosyası adı da kontrol edildi.

Yerel tarih kontrolünün dar alandaki genişlik davranışı için Chromium içinde en az 220 piksel kontrol genişliğiyle ek deneme yapıldı. Tarayıcı kontrolleri Chromium üzerinde çalıştı; fiziksel iPhone / Safari testi yapılmadı. Sağlık ve düzenleme pencerelerinin mobil, Sürü Merkezi’nin masaüstü ekran görüntüleri yerel olarak incelendi.

## Kapsam ve paket

2.0.34 tam kaynak paketi temel alındı. Sunucudaki bütün fonksiyon / sınıf gövdeleri önceki sürümle aynıdır; sunucuda yalnız App Edition yapı etiketi güncellendi. Kayıt işlemleri, veritabanı şeması ve hesaplama kuralları değiştirilmedi. Sürü Merkezi değişikliği sunum, ortak stiller ve liste ayarları özetinin canlı aramada güncellenmesiyle sınırlıdır.

Python ve JavaScript sözdizimi ile ZIP bütünlüğü ayrıca kontrol edildi. Önceki paketin bütün dosyaları korunur; bu sürümün değişiklik ve doğrulama notları eklenir. Kullanıcı veritabanı, lisans, bu çalışma sırasında oluşturulan test veritabanları ve tarayıcı ekran görüntüleri dağıtım paketine eklenmez.

ZIP, Windows kurulumunu GitHub Actions ile oluşturmak için tam kaynak projedir. Bu ortamda Windows EXE derlenmedi veya kurulu uygulamaya dağıtım yapılmadı.
