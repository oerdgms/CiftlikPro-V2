# Hotfix1.22y Solver Koruma Notu

Hotfix1.22y yalnızca düşük çözünürlük rasyon yerleşimi ve floating davranışını düzeltir. Solver/rasyon hesap fonksiyonları Hotfix1.22w tabanıyla değiştirilmemiştir.

# Solver Değişiklik ve Güvenlik Raporu

Bu rapor, `ÇiftlikPro Enterprise v3.9.23 DEV4 Hotfix1.22w` paketini kapsar. Paket, kullanıcının paylaştığı Hotfix1.22v arşivi üzerine hazırlanmıştır.

## Sonuç

- Solver sürümü: **DEV4.19.6**
- Kullanıcının seçtiği yemler korunur; günlük kilogramlar otomatik artırılıp azaltılır.
- GCAA açığı optimizasyon sıralamasında birinci besleme hedefidir.
- Enerji aramasında NEm/NEg yoğunluğu kullanılır; arpa, mısır silajı ve uygun besi yemi öne çıkarılır.
- Gereksiz HP fazlası daha erken cezalandırılır; hedef HP'nin %10 üzerindeki arz kademeli azaltılır.
- GCAA hedefinin %0,5 altında kalan sonuç **Sınırlı çözüm** olarak kaydedilmez.
- Hedef yakalanamazsa uygulama çözüm kaydetmez ve engelleyen sınırı açıklar.
- Nişasta ideal/dikkat bantları faza göre genişletildi; `%45` genel sert güvenlik kapısıdır.
- NDF/eNDF, mineral, toplam tahıl, buğday ve kaba/kesif güvenlik kapıları korunur.
- Hotfix1.19h yalnız kullanım katmanına kalıcı yem kilidi, KM payı, yaş/dönem ön kontrolü, değişiklik özeti ve hedef şeritleri ekler; optimizer sıralaması ve hedef aralıkları değişmez.
- Hotfix1.22f yalnız MISIR PULU katalog/migrasyon verisini ve mobil yem simgesi sunumunu düzeltir; 10 solver/hedef fonksiyonunun normalize kaynak özeti önceki 1.22e paketiyle birebir aynıdır (`f8d234366c31bdd1f1f943265d397bd328be9fb4518d5a93e6be28bd6dd308e0`).
- Hotfix1.22g yalnız mobil yem ve hedef kartlarının responsive sunumunu değiştirir; solver matematiği ve hedef değerleri aynıdır.
- Hotfix1.22h yalnız iOS/Safari çift simge katmanını ve masaüstü hedef kartlarının ilk açılış sıçramasını temizler; hesap ve solver kodu değişmez.
- Hotfix1.22i mobilde kalan hücre pseudo-logosunu ve sıra rozetini kaldırır; hesap ve solver kodu değişmez.
- Hotfix1.22j yalnız Dashboard mobil düzenini ve stok özeti sorgusunu düzeltir; rasyon hesap ve solver kodu değişmez.
- Hotfix1.22k yalnız Dashboard görünüm seçimini ve sayfa sunumunu değiştirir; rasyon hesap ve solver kodu değişmez.
- Hotfix1.22q Dashboard görünüm seçimini, toplu padok-rasyon atamasını, padok ek yem/takviye ve buzağı iç üretim maliyeti katmanlarını ekler. Solver DEV4.19.6 matematiği ve bilimsel hedefleri değişmez.
- Hotfix1.22v düşük çözünürlük rasyon sunumunu, Yem Kataloğu sıralama/filtrelemeyi ve fiziksel stok eşitlemeyi ekler; 28 solver/rasyon ilişkili üst-seviye fonksiyon Hotfix1.22u ile AST olarak birebir aynıdır.
- Hotfix1.22w düşük çözünürlük bilimsel ayrıntı görünürlüğünü, katalog aramasını, tarih-etkin günlük kullanımı, gelecek tarihli atamayı ve tarihsel stok sayımını düzeltir. Hotfix1.22v tabanındaki 28 solver/rasyon ilişkili üst-seviye fonksiyon AST olarak birebir aynıdır (`a263d9db8bae80e39276bc89cacecb6cf25b137a4e40e60e501846470c984843`).

## Değiştirilen alanlar

| Alan | Hotfix1.19h davranışı |
|---|---|
| `solve_smart_ration` | GCAA öncelikli enerji/HP takası ve tam hedef kayıt kapısı |
| `make_seed` enerji modu | NEm/NEg yüksek, HP/nişasta yükü düşük yemleri öne çıkarır |
| `hard_safety_vector` | Enerji hedefi uğruna ciddi KM/HP sapmasına izin vermez |
| `beef_starch_targets` | Faz bazlı ideal/dikkat bantları ve `%45` genel güvenlik sınırı |
| `_solver_feasibility_report` | Dikkat bandını uyarı, yalnız genel sınırı sert ret olarak uygular |
| Çalışma Masası durumu | Uyarılı sonuç yeşil “Çözüldü” görünmez |

## Doğrulama senaryosu

`275 kg / 1,40 kg GCAA / yaş boş` ve seçili altı standart yemle:

- GCAA kapasitesi: **1,395 kg/gün** (iki ondalık gösterimde 1,40)
- HP: **%14,6**
- Kaba yem KM: **%52,6**
- Nişasta: **%24,0**
- Fizibilite: **Uygun**

## Kesin ret olarak kalan durumlar

- GCAA açığının %0,5'i aşması
- `%45` genel nişasta sınırı veya nişasta/eNDF birlikte yüksek göreli rumen riski
- Ciddi NDF/eNDF yetersizliği
- Güvenli pencere dışındaki Ca:P veya mineral sert üst sınırı
- Toplam tahıl/buğday sert güvenlik sınırı
- Ciddi KM veya HP tabanı sapması
