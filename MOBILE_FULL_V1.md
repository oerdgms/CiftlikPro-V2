# ÇiftlikPro Mobile Full V1 — Hotfix1.22ct

Bu paket MobileAPI18 tabanını korur ve mobil saha arayüzüne **Modüller** merkezi ekler.

## Korunan mobil-native saha işlevleri
- Fotoğraflı kompakt aktif sürü ve padok listeleri
- Hayvan / buzağı ekleme ve düzenleme
- Alış fiyatı ve finans bağlantısı
- Fotoğraf çekme, galeri ve büyütme
- Tartım, sağlık, not, üreme, doğum
- Satılan / kesilen / ölen-kayıp arşivi
- Sağlık Merkezi ve Üreme Merkezi hızlı mobil ekranları

## Full V1 Modül Merkezi
Mobil alt menüde **Modüller** sekmesi eklendi. Aynı ÇiftlikPro sunucusundaki mevcut modüllere doğrudan erişim sağlar:
Finans, Yem & Stok, Rasyon, Raporlar, Sağlık, Üreme, Padok Yönetimi, Süt, Tarım ve Tam Dashboard.

Bu bağlantılar yeni/ayrı veri üretmez; mevcut masaüstü modüllerini ve aynı veritabanını kullanır. Solver mantığı değiştirilmemiştir.

## Güvenlik düzeltmesi
Hayvan düzenleme ekranında mevcut TR küpe numarasının rakam bölümü render sonrasında da tekrar atanarak boş/eksik görünme regresyonuna karşı korunmuştur.
