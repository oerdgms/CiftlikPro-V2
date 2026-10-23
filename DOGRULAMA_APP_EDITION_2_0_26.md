# App Edition 2.0.26 — Doğrulama

Tarih: 22/10/2026. Kapsam: Sürü Merkezi durum düzenleme bağlantısının adlandırılması ve görünümü.

## Tamamlanan kontroller

- App Edition görünüm/paket testleri: 29 başarılı.
- Mobil/masaüstü bütünlük testleri: 13 başarılı.
- Değişen Python modüllerinin sözdizimi kontrolü başarılı.
- Önceki tam paketle karşılaştırmada app/server.py dosyasında yalnız yapı kimliği değiştiği doğrulandı.

Linux başsız Chromium / Playwright ve ayrı deneme veritabanında:

- Tümü, Sağmal, Kuru, Düve, Gebe ve Kızgın filtreleri açıldı. Her satırda “Laktasyonda” rozetinin yalnız manuel durumu lactating olanlarda bulunduğu doğrulandı. Düzenleme bağlantısının görünen adı “Durumu düzenle”.
- Kuru ve Gebe olarak kayıtlı örneğin bu iki rozeti gösterdiği ve bağlantının doğru hayvanın Kuru seçili düzenleyicisini açtığı doğrulandı.
- 1024, 1280, 1322, 1366 ve 1600 pikselde Ayrıntı, Kart ve Kompakt görünümleri kontrol edildi. 15 görünümde 28'er satır, toplam 420 satır ölçüldü. Görüntüle/Düzenle/Sil düğmelerinin hizası ve boyutları korundu; yeni bağlantı kendi hücresine sığıyor.
- Sayfa düzeyinde yatay taşma yok. Kart görünümünde gereksiz yatay kaydırma yok. Filtrele/Temizle düğmeleri aynı hizada.
- Görüntüle, Düzenle ve durum bağlantısı doğru hedefi açtı. Silme onayı iptal edildiğinde silme isteği gönderilmedi.
- 390 ve 768 pikselde mobil Sağmal listesi doğru sayıyı gösterdi ve yatay taşma oluşmadı.
- JavaScript sayfa hatası: 0. Kuru/Gebe örneğinin Kompakt görünümü gözle incelendi.

## Kapsam

Kayıt ve hesaplama mantığı değiştirilmedi. Bu sürüm için ilgili görünüm ve paket testleri çalıştırıldı; tam regresyon tekrar edilmedi. Windows EXE bu ortamda derlenmedi; mevcut GitHub Actions akışıyla oluşturulur.

Tam kaynak ZIP'i işletme veritabanı, QA betiği, tarayıcı bağımlılığı veya Python önbelleği içermez. Önceki mobil sekme ve masaüstü düğme hizası düzeltmeleri pakete dahildir.
