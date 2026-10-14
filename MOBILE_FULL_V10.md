# ÇiftlikPro Mobile Full V10

Enterprise çekirdeği: **V3.9.23 DEV4 Hotfix1.22cr** (değişmedi)

Mobil build: **MobileFullV10-ReferenceUI-FieldModules**

## V10 kapsamı
- Mobil uygulama kabuğunda yatay sayfa taşması kilitlendi; ekran gövdesi yalnız dikey kaydırılır.
- Referans görünüme göre yeşil başlık, kart, chip, padok ve modül listesi sıkılaştırıldı.
- Finans başlığındaki toplam `kayıt` rozeti kaldırıldı; çalışan finans kayıt backend'i korundu.
- Sağlık Merkezi: sağlık kaydı, plan oluşturma, bugün/geciken/yaklaşan/tümü ve geçmiş düzenle/sil korunur.
- Rasyon: mobil arama, detay, yem miktarı düzenleme ve padok ataması; solver mantığına dokunulmadı.
- Yem & Stok: mobil arama, stokta olan/azalan filtreleri ve stok giriş/çıkış akışı.
- Üreme Merkezi: mobil filtreler ve mevcut üreme verisi/işlemleri korunur.
- Padok: referans tipi tek satır kartlar, doluluk göstergesi ve tekli/toplu padok taşıma akışı korunur.

## Koruma
- `APP_VERSION = 3.9.23 DEV4 Hotfix1.22cr` olarak kalır.
- Mevcut veritabanı ve `static/uploads` içeriği değiştirilmez/silinmez.
