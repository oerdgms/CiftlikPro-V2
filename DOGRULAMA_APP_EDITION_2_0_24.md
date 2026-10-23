# App Edition 2.0.24 — Doğrulama

Tarih: 22/10/2026. Kapsam: mobil hayvan/buzağı detayında sekme şeridinin sabitlenmesi.

## Tamamlanan kontroller

- App Edition / görünüm testleri: 29 başarılı.
- Referans mobil ekran testleri: 12 başarılı.
- Masaüstü/mobil bütünlük testleri: 13 başarılı.
- Rasyon taslağı ve sağlık ajandası JavaScript testleri: başarılı.
- Değişen Python/JavaScript kaynaklarının sözdizimi kontrolü: başarılı.

Linux başsız Chromium / Playwright üzerinde, ayrı deneme veritabanıyla:

- 320, 390, 430, 768 ve 900 pikselde hayvan ve buzağı detayları açıldı.
- Her görünümde 30 ardışık yukarı/aşağı kaydırma örneği; toplam 300 ölçüm. Sabitlenmiş şeridin üst başlıkla hizası değişmedi. Sabitlenme nedeniyle içerik konum değişimi 0 piksel.
- Yatay kaydırılarak Geçmiş sekmesine erişildi; tıklama ve seçili sekme doğru çalıştı.
- Üst geri düğmesi özeti geri getirdi; şerit doğal konumuna döndü. Tek şerit kaldığı doğrulandı.
- 640/780/700/844 piksel yükseklik değişimlerinde ve 78 piksel başlık yüksekliği kontrolünde hizalama korundu.
- Sabitleme sınırı art arda iki yönde geçildi; yuva konumu kaymadı.
- 1366 pikselde masaüstü içerikleri görünür, mobil sekmeler gizli kaldı.
- JavaScript sayfa hatası: 0. Sabitlenmiş şerit görüntüsü gözle incelendi.

## Kapsam sınırı ve paket

Bu sürümde kayıt/hesaplama mantığı değişmediği için ilgili görünüm ve bütünlük testleri tekrarlandı. Önceki sürümün tam regresyon bilgisi DOGRULAMA_APP_EDITION_2_0_23.md dosyasındadır. Bu sürüm için tüm regresyon paketinin yeniden çalıştırıldığı iddia edilmez.

Bu ortamda fiziksel iPhone/Safari ve Windows EXE testi yapılmadı. Kontroller Chromium ile mobil ölçülerde gerçekleştirildi. Kullanıcının gerçek cihazında Safari kaydırma görüntüsünün kontrolü gerekir.

app/server.py dosyasında yalnız yapı kimliği değişmiştir. ZIP kişisel işletme verisi, test veritabanı, QA betikleri, tarayıcı bağımlılığı ve Python önbelleği içermez. Windows kurulum hedefi CiftlikPro_Enterprise_V3_9_23_DEV4_AppEdition_2_0_24_Setup.exe.
