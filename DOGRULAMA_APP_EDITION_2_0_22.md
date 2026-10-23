# App Edition 2.0.22 — Doğrulama

22/10/2026. Kullanıcının manuel laktasyon ve Erkek kartı talepleri.

## Kayıt ve regresyon

- 381 Python testi çalıştırıldı. İlk taramada 380 test geçti; gerçek barkod testi ortamda zxing-cpp bulunmadığından başarısız oldu. requirements.txt içindeki zxing-cpp 2.3.0 kurulduktan sonra ilgili 24 testin tamamı (gerçek QR ve DataMatrix dahil) başarıyla tekrar çalıştırıldı. Böylece 381 testin tümü doğrulandı.
- Yeni manuel laktasyon testleri: 15/15 başarılı. Süt/doğumdan üyelik çıkarmama; seçili 12 hayvanda özet/liste/detay tutarlılığı; erkek ve buzağı sayılarının ayrımı; 30/305 günlük otomatik sona erme olmaması; bilinmeyen başlangıç/sıranın boş kalması; geçersiz seçim/tarihte atomik geri alma; mevcut kuruya çıkarma tarihiyle uyum; geçmiş; güncelleme sonrası kayıt korunumu; silmede temizlik; oturum/lisans ve HTTP toplu kayıt kontrol edildi.
- App Edition entegrasyon testleri 23/23 başarılı; çekirdek kayıt ve solver kaynak koruma testi geçti.
- Rasyon taslağı ve sağlık ajandası JavaScript testleri başarılı.
- Değişen Python modülleri ve JavaScript dosyalarında sözdizimi kontrolü başarılı.

## Tarayıcı

Linux başsız Chromium / Playwright ile gerçek uygulama sunucusu ve ayrı deneme veritabanı kullanıldı.

- İlk ekranda hayvan seçimi boş; laktasyon başlangıcı boş.
- 12 dişi elle seçildi; kaydedilip Sağmal listesinde ve ana sayfada 12 olarak tekrar okundu. Süt girişleri seçimi kendiliğinden oluşturmadı.
- Aramada görünmeyen seçili hayvanların seçimi korundu.
- Erkek kartı gerçek aktif erkek sayısını gösterdi; tıklama aynı sayıda yetişkin erkek kaydını listeledi.
- Başlangıç bilinmiyorken mobil özette sağım günü boştu. 01/10/2026 ve ikinci laktasyon girilince 22/10/2026 tarihinde 21 gün olarak görüntülendi.
- 320, 390, 768, 1024 ve 1366 pikselde toplu/tekli laktasyon, ana sayfa ve erkek listesi kontrol edildi: 20 yerleşimde yatay taşma yok.
- JavaScript sayfa hatası: 0.
- Mobil manuel ekran ve ana sayfa görüntüleri gözle kontrol edildi.

## Paket

app/server.py dosyasında 2.0.21'e göre yalnız mobil yapı kimliği değişti. Yeni veri modeli ve HTTP işlemleri dairy_management modülünden bağlanıyor. PyInstaller modülü ve dairy.js dosyasını içerir; Actions kaynak/EXE smoke listeleri güncellendi. ZIP kullanıcı verisi, deneme veritabanı, QA sunucusu, tarayıcı bağımlılığı ve Python önbelleği içermez.

Windows EXE bu ortamda derlenmedi; fiziksel iPhone/Android testi yapılmadı. Tam kaynak ZIP içindeki GitHub Actions iş akışı Windows kurulum dosyasını üretir.
