# ÇiftlikPro Enterprise v3.9.20 — GitHub Source

Temiz kaynak tabanı. Kullanıcı arayüzünde HOTFIX, DEV veya port bilgisi gösterilmez.

## Rasyon motoru

Besi solverı, kullanıcının seçtiği yemlerin **kg/baş/gün miktarlarını karar değişkeni** olarak ele alır. `Besi_V5.02.xlsm` içindeki Solver davranışı incelenerek kısıt-öncelikli bir optimizasyon sırası uygulanmıştır:

1. Rumen ve besleme güvenliği: NDF/eNDF, nişasta, pH ve mineral sınırları.
2. Dört saha kartı birlikte: Kuru Madde, Ham Protein, Metabolik Enerji ve Kaba/Kesif oranı.
3. Dört kart için yaklaşık ±%3,5 tolerans hedeflenir; tek kartı kusursuzlaştırıp diğerlerini bozmak avantaj sağlamaz.
4. Seçilen normal yemler korunur; miktarları yemlerin günlük kullanım sınırları içinde otomatik değiştirilir.
5. Maliyet yalnız besleme hedeflerinden sonra son seçim kriteridir.

Akıllı Süt Rasyonu aynı `feed_catalog` verisini kullanır ve canlı ağırlık + hedef süt üzerinden ayrı süt ihtiyaç motoruyla çözülür.

## Kaynaklar

- `app/server.py`
- `app/feed_catalog.json`
- `app/desktop_launcher.py`
- `docs/BESI_SOLVER_REFERANS.md`
- `docs/SUT_SOLVER_REFERANS.md`
- `CHANGELOG.md`

`KAYNAKTAN_CALISTIR.bat` kaynak koddan yerel çalıştırma içindir; kullanıcı arayüzünde port veya geliştirme etiketi gösterilmez.

> Rasyon sonuçları karar-destek amaçlıdır. Gerçek yem laboratuvar analizleri katalog referanslarından önceliklidir.
