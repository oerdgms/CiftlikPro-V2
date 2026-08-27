## v3.9.20 Solver DEV4.1
- Sidebar `🐄 ÇiftlikPro` marka alanı yatay+dikey merkezlendi.
- Otomatik canlı ağırlık → besi dönemi seçimine manuel override eklendi.
- Faz kaba/kesif koridorları manuel seçimde de solver sınırlarına uygulanıyor.
- Ca/P aşım cezası güçlendirildi.
- GitHub/Windows installer dosyaları korundu.

# ÇiftlikPro Sürüm Notları

## v3.9.20 — 6.17 kaynak tabanı

- `Besi_V5.02.xlsm` formül/kısıt yapısı incelenerek besi solverı kısıt-öncelikli hale getirildi.
- Seçilen yemlerin miktarları aynı anda optimize edilir; kullanıcı manuel +/− ile rasyon kurmak zorunda değildir.
- Kuru Madde, Ham Protein, Metabolik Enerji ve Kaba/Kesif oranı yaklaşık ±%3,5 saha toleransında birlikte değerlendirilir.
- Solver sıralaması güvenlik → dört saha kartı → pratik miktarlar → maliyet şeklindedir.
- Seçilen normal yemler sonuçtan sessizce çıkarılmaz; katkı/mineral kalemleri kendi doz kurallarına göre sıfıra inebilir.
- NDF/eNDF, nişasta, tahmini rumen pH ve mineral sınırları ayrı güvenlik raylarıdır.
- Akıllı Süt Rasyonu ve 6.16 UX düzeltmeleri korunur.
- Arayüzde HOTFIX / DEV / PORT gibi geliştirme etiketleri kaldırıldı; sade `v3.9.20` görünümü kullanılır.

## 6.17 Desktop ERP Final — 2026-08-25
- DEV3 referans rasyon yerleşimi korundu.
- Desktop ERP görsel standardı tüm ana modüllere yayıldı.
- Tablo, form, filtre, kart ve araç çubuğu yoğunluğu ERP kullanımına göre standardize edildi.
- Solver, DB, login, LAN/Tailscale ve sunucu başlatma davranışına dokunulmadı.

## Desktop ERP DEV6 · 2026-08-26
- Mobilde alt sayfalardan Dashboard'a dönüş için üst ÇiftlikPro ana sayfa bağlantısı görünür hale getirildi ve hamburger menü korundu.
- Mobil hızlı işlem şeridi yatay kullanılabilir tutuldu; finans filtre/arama/Temizle taşmaları responsive düzeltildi.
- Hayvan satış/kesim çoklu seçim özetinde "Hayvan Başı Gelir" ifadesi netleştirildi; küpe butonları standart ERP stilinde korunuyor.
- Dashboard'daki tekrar eden küçük ÇiftlikPro metni kaldırıldı; çiftlik logosu/başlığı ana sayfa bağlantısı oldu.
- Ayarlar, yalnız Çiftlik Profili yerine program genelindeki ayarlara giriş sağlayan Ayarlar Merkezi olarak düzenlendi.
- Dashboard'un 8 özet kartı korundu; alt alan kompakt "Bugünün İşleri" (kızgınlık, gebelik/aşı, finans) panellerine dönüştürüldü.
- Solver, veritabanı, LAN/Tailscale ve 8953 ağ başlatma davranışı değiştirilmedi.


## Solver DEV4
- Canlı ağırlığa göre otomatik besi dönemi seçimi korunup faz oranları saha standardına göre revize edildi.
- Başlangıç: %50/%50; Geliştirme: %40/%60; Bitirme: %30–40/%60–70 (KM bazında).
- Faz kaba/kesif koridoru eNDF/pH güvenlik raylarından önce uygulanıyor.
- Kaba/kesif kartında sınırdaki yuvarlama kaynaklı yanlış “yüksek/düşük” uyarısı için tolerans eklendi.
- Hedef bağlamında besi dönemi ve faz kaba/kesif koridoru gösteriliyor.
