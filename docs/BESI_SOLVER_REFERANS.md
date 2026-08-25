# Besi Solver Referansı — Besi_V5.02.xlsm

Bu belge, kullanıcının sağladığı `Besi_V5.02.xlsm` çalışma kitabının davranışsal referans olarak incelenmesiyle oluşturulmuştur. Orijinal Excel dosyası GitHub kaynak paketine dahil edilmez.

## Excel'den taşınan temel fikirler

- Yem miktarları Solver karar değişkenleridir; hedef kartları elle ayarlanan sabit reçete değildir.
- Yemlerin günlük alt/üst kullanım sınırları korunur.
- DMI/Kuru Madde, enerji ve protein hedefleri birlikte değerlendirilir.
- Kaba/kesif dengesi ve fiziksel lif, rumen güvenliğinin ana taşıyıcılarıdır.
- Bir hedefteki iyileşme başka bir hedefte büyük bozulma yaratıyorsa çözüm daha iyi sayılmaz.
- Saha toleransı kullanılır; laboratuvar tipi sıfır sapma aranmaz.

## ÇiftlikPro 6.17 uygulaması

Besi solverı lexicographic (öncelik sıralı) bir değerlendirme uygular:

1. **Güvenlik ihlali sayısı ve büyüklüğü** — NDF/eNDF, nişasta, rumen pH, Ca:P ve aşırı mineral.
2. **Dört ana kartın tolerans dışı kalma sayısı** — KM, HP, ME, kaba/kesif.
3. **En kötü kart sapması** — tek bir kartın diğerlerinin pahasına bozulmasını engeller.
4. **Toplam normalize sapma** — hedeflerin birlikte yakınsamasını sağlar.
5. **Pratik yem miktarı cezası** — sahada anlamsız çok küçük normal yem miktarlarını azaltır.
6. **Maliyet** — yalnız yukarıdaki kriterler eşit düzeydeyse tercih sebebidir.

Optimizasyon başlangıçta farklı kaba/kesif payları ve enerji/protein/maliyet ağırlıklı tohumlar üretir; ardından iki yem arasında aynı KM'yi takas eden iteratif arama ile yem miktarlarını birlikte dengeler.

## Bilerek birebir kopyalanmayanlar

Excel'deki tüm hücre düzeni, makrolar veya arayüz kopyalanmamıştır. Amaç Excel'in karar mantığını web uygulamasına daha şeffaf ve otomatik bir biçimde taşımaktır.
