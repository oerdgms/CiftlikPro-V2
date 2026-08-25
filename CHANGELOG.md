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

## Desktop ERP DEV — Bugünün İşleri + Merkezi Ayarlar
- Dashboard: 8 durum kartı korunur; alt bölüm `Bugünün İşleri` (Kızgınlık / Gebelik Aşı / Finans) olarak sadeleştirildi.
- Ayarlar: üst menü `/settings` merkezine bağlandı; işletme, dashboard, kullanıcı, SMTP, veri/yedek, lisans ve besi ayarları tek merkezde toplandı.
- Sol menüde ikinci ÇiftlikPro yazısı kaldırıldı; ana ÇiftlikPro logosu Dashboard bağlantısı olarak kaldı.
- Dashboard sekme başlığı kaldırıldı.
- Hayvan küpe bağlantıları tüm listelerde standart ERP buton diline yaklaştırıldı.
- Finans toplu satış/kesim seçiminde `Toplam Tutar` ve `Hayvan Başı Gelir` ayrı gösterilir.
- Solver, DB, LAN/Tailscale ve 8953 başlatma altyapısı değiştirilmedi.

## GitHub final temizlik
- Python cache/bytecode dosyaları paketten çıkarıldı.
- Geçici DEV README dosyaları kaldırıldı.
- GitHub için sade README oluşturuldu.
- Çalışan uygulama kaynakları ve solver referans dokümanları korundu.
