# App Edition 2.0.27 — Doğrulama

Tarih: 22/10/2026. Kapsam: ortak Durum Ekle penceresi, yeni form sunumu ve mevcut kayıt yollarıyla bağlantıları.

## Otomatik kontroller

Tam Python taramasında 399 test çalıştırıldı. 398 test başarılıydı; gerçek QR/DataMatrix testi ortamda zxing-cpp bulunmadığından hata verdi. Mevcut proje bağımlılığı ortama kurulduktan sonra aynı QR/DataMatrix testi tek başına tekrar çalıştırıldı ve başarılı oldu. Uygulama kodu veya test beklentisi bu hata için değiştirilmedi.

Yeni hayvan işlem penceresi testleri 5/5 başarılı; son ikon güncellemesinden sonra da tekrarlandı. Tür/cinsiyet uygunluğu, pasif/aktarılmış kayıtların engellenmesi, geçersiz kimlikler, GET çağrılarının kayıt oluşturmaması, gerçek son tohumlamaya bağlı sonuç formu, kapanmış doğum sonucunun yeniden açılmaması, anne/buzağı bağlamı ve kullanıcı metninin HTML’den kaçırılması kontrol edildi.

Yeni fragment adresi normal HTTP sunucusunda kontrol edildi: oturumsuz istek girişe; lisansı kapalı oturum lisansa yönlendirildi. Yetkili oturumda içerik başarıyla geldi.

Değişen Python/JavaScript sözdizimi ve ortak CSS parantez dengesi kontrol edildi. Önceki paketle karşılaştırmada app/server.py içinde yalnız yapı kimliği değiştiği doğrulandı.

## Tarayıcı kontrolleri

Linux başsız Chromium / Playwright, ayrı deneme veritabanı:

- 1024, 1322 ve 1600 pikselde Kompakt, Ayrıntı ve Kart: 9 görünüm, 28’er satır; toplam 252 satır ölçümü. Görüntüle/Düzenle/Sil aynı sırada ve hizada, 34 piksel yükseklikte. Durum Ekle kendi hücresine sığıyor.
- Menü ve doğum formu bu genişliklerde ekran içinde kaldı. 390 ve 768 pikselde mobil hayvan kartından aynı pencere açıldı; yatay taşma yok.
- Escape, Vazgeç, formdan geri dönüş ve açan düğmeye odak dönüşü çalıştı. Boş doğum formu yerel doğrulama nedeniyle gönderilmedi; Kaydet kullanılabilir kaldı.
- Menü ve formları açıp kapatma öncesi/sonrası hayvan, buzağı, kızgınlık, tohumlama, süt durumu geçmişi, tartım, süt ve finans kayıt sayıları aynı kaldı.
- Sağmal kaydı başlangıç/sıra ile saklandı; Kuruya geçiş doğru hayvana yazıldı ve gebelik sonucu korundu.
- Kızgınlık ve tohumlama doğru hayvana kaydedildi. Gebe ve Gebe Değil seçimleri en güncel gerçek tohumlamayı güncelledi.
- Doğum formu doğru anneye tek buzağı oluşturdu; geliş kaynağı Çiftlikte Doğdu, alış bedeli sıfır. Annenin gebeliği Doğum olarak kapandı. Manuel süt durumu ayrı kaldı.
- Erkek hayvanın tartımı doğru kayda yazıldı. Erkek ve buzağı menülerinde yalnız kart notu, sağlık ve tartım vardı.
- Sağlık bağlantısında doğru hayvan hazır seçildi; kart notu bağlantısında doğru hayvanın not alanı odaklandı.
- Bu denemeler süt ve finans kayıt sayısını değiştirmedi. JavaScript sayfa hatası: 0.
- Masaüstü ve telefon görüntüleri gözle incelendi. Son doğum/tohumlama ikonları ve Türkçe içerik 1322 ve 390 pikselde ayrıca kontrol edildi.

## Paket sınırları

Kontroller gerçek iPhone/Safari veya derlenmiş Windows EXE üzerinde yapılmadı. Tam kaynak ZIP’inde yeni Python modülü ve Windows paket tanımı bulunur; kurulum mevcut GitHub Actions akışıyla oluşturulur. Önceki mobil sabit sekme ve masaüstü düğme hizası düzeltmeleri korunur.

ZIP işletme veritabanı, deneme verisi, QA betikleri, tarayıcı bağımlılıkları veya Python önbelleği içermez.
