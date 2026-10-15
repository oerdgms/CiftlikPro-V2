# MobileAPI11 — Masaüstü Günlük İşlemler

MobileAPI10 tabanı korunarak mobil hayvan kartı masaüstündeki 360° hayvan kartına yaklaştırıldı.

## Eklenenler
- Hayvan detayında son tartımlar ve yeni **Tartım Ekle** işlemi.
- Aynı gün tartım tekrar girilirse masaüstü davranışıyla kayıt güncellenir.
- Hayvan detayında **Gelir / Gider / Net** finans özeti (ortak finance tablosundan).
- Hayvan fotoğraf galerisi verisi ve telefondan kamera/galeriden **Fotoğraf Ekle**.
- Mobil fotoğraf 15 MB sınırıyla alınır, EXIF yönü düzeltilir, WEBP'e optimize edilerek mevcut uploads + animal_photos altyapısına yazılır.
- Hayvan kartında kompakt Sağlık / Tartım / Fotoğraf hızlı işlemleri.

## Korunanlar
- Aktif sürü ve padok eşitliği.
- Sağlık kaydı ekle/düzenle/sil, planlı Uygulandı.
- Tohumlama / gebelik sonucu, notlar, yeni hayvan/buzağı, padok toplu sağlık.
- Detay açılışında scroll-top düzeltmesi.
