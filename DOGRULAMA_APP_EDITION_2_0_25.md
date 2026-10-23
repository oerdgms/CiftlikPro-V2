# App Edition 2.0.25 — Doğrulama

Tarih: 22/10/2026. Kapsam: masaüstü Sürü Merkezi satır/filtre düğmeleri.

## Tamamlanan kontroller

- App Edition görünüm/paket testleri: 29 başarılı.
- Masaüstü/mobil bütünlük testleri: son görünüm değişikliğinden sonra 13 başarılı.
- Rasyon taslağı ve sağlık ajandası JavaScript testleri: başarılı.
- Değişen Python ve referans JavaScript sözdizimi: başarılı.

Linux başsız Chromium / Playwright üzerinde, ayrı deneme veritabanında:

- 1024, 1280, 1322, 1366 ve 1600 pikselde; 626 piksel yükseklikte; sol menü açık olarak Ayrıntı, Kart ve Kompakt görünümleri kontrol edildi.
- 15 görünümde 28'er kayıt; toplam 420 satır ölçümü. Dişi, erkek ve buzağı satırlarının her birinde Görüntüle/Düzenle/Sil aynı sırada, aynı yatay konum farklarıyla ve aynı dikey hizada bulundu. Üç düğmenin yüksekliği 34 piksel.
- Laktasyon yalnız yetişkin dişilerin Durum hücresinde bulunuyor. Bağlantı tıklanıp doğru hayvanın düzenleyicisinin açıldığı doğrulandı.
- Görüntüle ve Düzenle doğru hayvan sayfasına gidiyor.
- Sil tıklaması onay penceresini açtı; iptal edilince silme isteği gönderilmedi.
- Filtrele/Temizle düğmeleri aynı üst hizadaydı; yükseklikleri 42 piksel.
- Kart görünümünde gereksiz yatay kaydırma yok; tüm masaüstü kontrollerinde sayfa düzeyinde yatay taşma yok.
- 390 ve 768 pikselde mobil Sağmal listesi görünür; masaüstü katmanı gizli; Sağmal sayısı 12 ve yatay taşma yok.
- JavaScript sayfa hatası: 0. 1322 pikselde Kompakt ve Kart görüntüleri gözle incelendi.

## Sınırlar ve paket

Bu sürümde kayıt/hesaplama mantığı değişmediğinden ilgili görünüm ve paket testleri tekrarlandı; tam regresyonun yeniden çalıştırıldığı iddia edilmez. Önceki sürümlerin kontrol bilgileri kendi doğrulama dosyalarında korunur. Windows EXE bu ortamda derlenmedi; kurulum mevcut GitHub Actions akışıyla üretilir.

app/server.py dosyasında yalnız yapı kimliği değişmiştir. ZIP kullanıcı işletme verisi, test veritabanı, QA betiği, tarayıcı bağımlılığı veya Python önbelleği içermez. 2.0.24 mobil sekme düzeltmesi bu pakette bulunmaktadır.
