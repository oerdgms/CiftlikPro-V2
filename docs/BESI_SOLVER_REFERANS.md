# Besi Solver Referansı — Besi_V5.02.xlsm

Bu belge, kullanıcının sağladığı `Besi_V5.02.xlsm` çalışma kitabının davranışsal referans olarak incelenmesiyle oluşturulmuştur. Orijinal Excel dosyası GitHub kaynak paketine dahil edilmez.

## Excel'den taşınan temel fikirler

- Yem miktarları Solver karar değişkenleridir; hedef kartları elle ayarlanan sabit reçete değildir.
- Yemlerin günlük alt/üst kullanım sınırları korunur.
- DMI/Kuru Madde, enerji ve protein hedefleri birlikte değerlendirilir.
- Kaba/kesif dengesi ve fiziksel lif, rumen güvenliğinin ana taşıyıcılarıdır.
- Bir hedefteki iyileşme başka bir hedefte büyük bozulma yaratıyorsa çözüm daha iyi sayılmaz.
- Saha toleransı kullanılır; laboratuvar tipi sıfır sapma aranmaz.

## ÇiftlikPro DEV4.12 uygulaması

Besi solverı lexicographic (öncelik sıralı) bir değerlendirme uygular:

1. **Ciddi güvenlik ihlali** — NDF/eNDF, toplam + rumende yıkılabilir nişasta, Ca:P ve aşırı mineral birlikte değerlendirilir. Klinik pH tahmini yapılmaz.
2. **Temel fizibilite** — KM, HP, ME, NASEM NEm/NEg’den karşılanabilir GCAA ve kaba/kesif.
3. **En kötü kart sapması** — tek bir kartın diğerlerinin pahasına bozulmasını engeller.
4. **Toplam normalize sapma** — hedeflerin birlikte yakınsamasını sağlar.
5. **Pratik yem miktarı cezası** — sahada anlamsız çok küçük normal yem miktarlarını azaltır.
6. **Maliyet** — yalnız yukarıdaki kriterler eşit düzeydeyse tercih sebebidir.

Tek başına “buğday %40”, “toplam tahıl %30” veya “fabrika yemi %35” gibi evrensel bir sert kısıt kullanılmaz. Bu oranlar yem işleme biçimi, toplam diyet, adaptasyon ve ürün formülüne göre değişir. Ürün etiketi/uzman dozu girilmişse kesin alt/üst sınır olarak uygulanır.

INRA değerleri NASEM hedeflerine çevrilip toplanmaz. UFV/PDI/PDIA/RPB, NDF sindirilebilirliği ve nişasta yıkılabilirliği ayrı veri alanlarıdır; DEV4.12’de aktif rumen-risk hesabında nişasta yıkılabilirliği, kalite/kapsam ekranında diğer INRA alanları kullanılır. Tam CNCPS karbonhidrat/protein fraksiyon motoru bu sürümde yoktur.

Optimizasyon başlangıçta farklı kaba/kesif payları ve enerji/protein/maliyet ağırlıklı tohumlar üretir; ardından iki yem arasında aynı KM'yi takas eden iteratif arama ile yem miktarlarını birlikte dengeler.

## Bilerek birebir kopyalanmayanlar

Excel'deki tüm hücre düzeni, makrolar veya arayüz kopyalanmamıştır. Amaç Excel'in karar mantığını web uygulamasına daha şeffaf ve otomatik bir biçimde taşımaktır.
