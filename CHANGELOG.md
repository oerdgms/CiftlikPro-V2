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
