# ÇiftlikPro Sürüm Notları

## V3.9.20 HOTFIX 6.16 DEV

Bu sürüm, HOTFIX 6.15 Clean Source tabanı korunarak hazırlanmıştır.

- Sürüm notları / kaynak geçmişi yeniden sabitlendi; önceki çalışma tabanı korunur.
- Finans kayıt tablosunda uzun açıklama/hayvan alanları satırı büyütse bile Düzenle ve Sil butonları tek sırada, kompakt ve sabit yükseklikte kalır.
- Rasyon Çöz penceresine Besi / Süt modu eklendi. Süt modu aynı Yem Kataloğu ve aynı veritabanını kullanır; temel girişler canlı ağırlık + hedef süt kg/gündür. Süt_V5.01.xlsm içindeki sağmal DMI yaklaşımı ve INRA/NASEM hedef mantığı sadeleştirilerek Süt Solver V1'e aktarılmıştır.
- Satılan ve kesilen hayvan listeleri dahil hayvan küpe numaralarında aynı `animal-tag-btn` görünümü ve mobil tablo standardı kullanılır.
- Mevcut HOTFIX 6.15 besi solver davranışı korunmuştur; bu paket besi solver matematiğini yeniden değiştirmez.
