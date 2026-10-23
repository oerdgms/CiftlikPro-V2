# App Edition 2.0.23 — Doğrulama

Tarih: 22/10/2026.

## Python ve JavaScript

- 394 Python testi çalıştırıldı. İlk tam taramada 393 başarılıydı; bir eski test masaüstünde tür açılır seçiminin bulunmamasını bekliyordu. Bu beklenti yeni ortak filtreyle uyumlu olarak güncellendi; seçili tür ve padok değerlerini doğrulayan kontroller eklendi. İlgili 7 araç çubuğu testi yeniden çalıştırıldı ve tamamı geçti.
- Yeni 13 mobil/masaüstü bütünlük testi son düzenlemeden sonra tekrar çalıştırıldı: tamamı geçti. Böylece 394 testin tamamı doğrulandı.
- 12 referans mobil ekran testi başarılı. Mevcut manuel laktasyon, finans/stok, rasyon/solver ve çekirdek kaynak koruma testleri tam taramada geçti.
- Rasyon taslağı ve sağlık ajandası JavaScript testleri başarılı.
- Python/JavaScript sözdizimi kontrolleri başarılı.

## Tarayıcı

Linux üzerinde başsız Chromium / Playwright, ayrı deneme veritabanı:

- Masaüstünde Sağmal 12 sayacı ve filtresi; 12 doğru satır; arama ve durum filtresinin birleşmesi.
- Masaüstü hayvan kartından laktasyon düzenleme; kaydetme ve yeni başlangıç/sıranın tekrar okunması.
- Süt merkezinde aynı Sağmal sayısı; sabah 12 L + akşam 13 L kaydedilip 25 L olarak tekrar okunması.
- Ana sayfada bölüm gizleme, kart sırası ve işlem sayısı tercihlerinin kaydedilmesi; aynı kullanıcıda mobil/masaüstü kart sırasının eşleşmesi.
- Beş işlem tercihiyle gerçekten beş görünür görev; tüm kartlar kaldırıldığında kaydın engellenmesi ve formun kullanılabilir kalması.
- Varsayılana Dön, gerçek buton tıklamasıyla test edildi. Mobil eski düzenleme bağlantısı yeni editöre yönlendi; masaüstü eski düzenleme bağlantısı yerinde kaldı.
- Modüller: 14 kutucuk her iki görünümde görünür. Mobil üç, geniş masaüstü dört sütun.
- 320, 390, 768, 1024, 1366 piksel genişliklerde ana sayfa, Sağmal listesi, hayvan detayı, düzenleyici, süt merkezi ve modüller: 30 yerleşimde yatay taşma yok.
- JavaScript sayfa hatası: 0.
- Masaüstü özet/liste ve mobil modüller/düzenleyici/süt merkezi görüntüleri gözle incelendi.

## Paket ve sınırlar

app/server.py dosyasında önceki sürüme göre yalnız yapı kimliği değişmiştir. Yeni sunum ve ayar yolları ayrı modüllerden bağlanır; mevcut süt kaydı POST yolu kullanılır. PyInstaller ve Actions yeni modül/varlıkları içerir. Paket kişisel işletme verisi, test veritabanı, QA betikleri, tarayıcı bağımlılığı ve Python önbelleği içermez.

Windows EXE bu ortamda derlenmedi; fiziksel iPhone/Android testi yapılmadı. ZIP tam kaynak/kurulum projesidir. Kurulum dosyası mevcut GitHub Actions iş akışıyla üretilir.
