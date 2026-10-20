# App Edition 2.0.9 — 20/10/2026 Mobil pencere düzeni

## Düzeltilen görünüm

- Üreme Merkezi üst durum filtresinde uzun başlıkların sayaçlara ve yan kutulara taşması giderildi.
- Filtreler mobilde iki sütundur; metin ve sayaç ayrı alanlarda durur, `Tümü` tam satır kullanır.
- Hızlı gebelik sonucu penceresindeki dört seçenek iki sütuna ayrıldı; alt işlemler uzun içerikte de erişilebilir kaldı.

## Kontrol edilen pencereler

- Hızlı işlem alt sayfası
- Irk seçimi ve QR/2D kamera sayfası
- Dashboard kart seçimi
- Sağlık planı çekmecesi
- Finans kayıt çekmecesi ve yem faturası önizlemesi
- Rasyon ekleme/çözme ve hızlı yem ekleme pencereleri
- İlaç/veteriner kayıt çekmecesi
- Padok taşıma penceresi
- Fotoğraf büyütme görüntüleyicisi

Bu alanlarda ekran yüksekliği `100dvh` üzerinden sınırlandı, iOS/Android güvenli üst-alt boşlukları eklendi ve uzun içerik ana sayfayı büyütmek yerine kendi penceresi içinde kaydırıldı. Kapatma düğmeleri en az 44 × 44 px tutuldu.

## Korunan alanlar

Enterprise çekirdeği `3.9.23 DEV4 Hotfix1.22cr` olarak kalır. Üreme sınıflandırması, doğum/gebelik kuralları, finans ve maliyet hesapları, kayıt yolları, veritabanı şeması, rasyon solver ve masaüstü görünümü değiştirilmedi.

Bu paket tam kaynak pakettir; hazır EXE içermez. Windows kurulum dosyası GitHub Actions üzerinden `CiftlikPro_Enterprise_V3_9_23_DEV4_AppEdition_2_0_9_Setup.exe` adıyla üretilir.
