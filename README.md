# ÇiftlikPro v3.9.20 — Solver DEV4.19 Son Kilitleme

DEV4.19, seçilen kaba ve kesif yemlerin tamamını uygulanabilir alt miktarda
rasyonda tutar ve miktarlarını besin değerlerine göre yeniden dengeler. Fazın
kaba/kesif koridorunu ciddi aşan aday, toplam tahıl faz üst sınırını aşan aday
ve buğdayın tahıl KM içindeki payı `%32` üstüne çıkan aday kaydedilmez. `%30–32`
buğday payı yalnız küçük sapma olarak “sınırlı” kabul edilir. Sunar 15.26 için
`10 kg`, Kardelen 19.27 için `6–12 kg` etiket sınırları kesin korunur. 250, 350
ve 500 kg besi ile 25 litre süt senaryoları kalıcı regresyon kapısındadır.

DEV4.18, 19–20 Ağustos 2026 tarihli gerçek ürün etiketlerini Yem Kataloğu'na
işler. `Sunar 15.26 Geliştirme Besi Yemi` ile `Sunar Kardelen 19.27 Süt Yemi`
adları, etiket HP/yağ/selüloz/kül/sodyum değerleri ve kuru madde dönüşümleri
güncellenmiştir. Kardelen'in `6–12 kg/baş/gün` etiket sınırı artık süt
solverında da kesin uygulanır. NDF, nişasta, Ca/P ve KM etikette bulunmadığı için
referans tahmin olarak açıkça ayrılır.

DEV4.17, faz nişasta üst sınırını kayıt kapısı yapar; besi yemi varken süt
yemini çözümden çıkarır ve enerjiye göre GCAA kapasitesini hedefin `%1`
çevresinde tutar. Güvenli ve hedefe yakın bir aday bulunamazsa yanlış rasyonu
kaydetmek yerine sınırlayan kısıtları kullanıcıya bildirir.

DEV4.16, hedefleri karşılayan adaylar arasında nişasta ideal bandını,
buğday/tahıl KM dengesini ve hayvan profiline uygun ticari yem kullanımını
maliyet ve genel çeşitlilikten önce değerlendirir. DEV4.15 Sunar yem profilleri
ve etiket alanları korunmuştur.

Bu paket, DEV4.14 rasyon güvenlik düzeltmelerine ek olarak kullanıcının gerçek
Sunar 15.26 ve Kardelen 19.27 etiketlerini, ayrıca Sunar Buzağı Büyütme Özel
Dönem Yemi'ni Yem Kataloğu'nda tutar. Üreticinin yayımlamadığı analiz alanları
tahmin olarak açıkça işaretlenir; kesin etiket değeri gibi sunulmaz. Ürün
etiketindeki değerler ayrı alanlarda aynen saklanır; solverın kullandığı besin
alanları ise kuru madde bazındadır.

Sunar Kardelen için güncel etiketteki `6–12 kg/baş/gün`; Buzağı Büyütme için
60–120 gün ve serbest tüketim bilgisi kaynak notunda yer alır. Mevcut
kullanıcı/laboratuvar analizleri korunur.

## DEV4.13 Bilimsel Hedef Kartları

Bu paket, besi hedef kartları ile solverın aynı bilimsel hesap kaynağını kullanmasını sağlar:

- DEV4.13 Hotfix 1, saha testinde görülen 1,24/1,30 GCAA kartının yanlış yeşil görünmesini düzeltir; minimumun altındaki anlamlı her sapma açıkça gösterilir.
- eNDF ile kaba yem KM payı ayrı yorumlanır; %24,0 ideal sınırının en çok 0,5 puan üzeri ölçüm/yuvarlama tamponunda “Sınırda” olarak değerlendirilir.
- Mobilde uzun çözüm açıklaması kısa özet halinde başlar; bilimsel ayrıntılar kullanıcı isterse açılır.
- “Besi Erkek” seçimi NASEM Chapter 20 Table 20-2 büyüyen tosun/boğa profiline; düve ve kastre erkek seçimi Table 20-1 profiline bağlanır.
- Kuru madde hedefi, rasyonun gerçek NEm yoğunluğundan canlı hesaplanır; kart ve solver aynı değeri kullanır.
- HP, Ca ve P kartları eşitlik hedefi değil **minimum gereksinim** olarak değerlendirilir. Makul hedef üstü arz yanlış “fazla” hatası üretmez.
- Toplam ME kartı ana karar kartından çıkarılmıştır. Enerji yeterliliği, NEm/NEg’den hesaplanan **GCAA kapasitesi** ile gösterilir.
- INRA 2018 yem alanları NASEM değerlerine karıştırılmaz; yalnız veri kapsamı ve fermantasyon doğrulamasında kullanılır.
- Tek bir eNDF denkleminden “tahmini rumen pH” üretilmez. Toplam nişasta, bilinen nişasta yıkılabilirliği ve eNDF ile göreli asidoz riski gösterilir.
- Evrensel tahıl, buğday veya fabrika yemi yüzdesi sert kısıt değildir. Ürün etiketi/uzman dozu girilmişse kesin sınırdır.
- Güvensiz, GCAA hedefini ciddi kaçıran veya KM ile hedef büyümeyi yapay biçimde telafi eden reçete kaydedilmez; sınırlayan kısıt açıklanır.
- Mobil/masaüstü rasyon görünümü, raporlar, hayvan aktarımı ve GitHub kurulum iş akışı korunmuştur.

# ÇiftlikPro v3.9.20 — Solver DEV4

Bu geliştirme sürümü, besi rasyonu solverında **canlı ağırlık → besi dönemi → faz kaba/kesif koridoru → rumen güvenliği → besin hedefleri → kalite/maliyet** sırasını uygular.

## Faz standardı (KM bazında)

- **Besi Başlangıç:** 200–299 kg referansı, hedef yaklaşık **%50 kaba / %50 kesif** (solver koridoru %47–53 kaba).
- **Besi Geliştirme:** 300–449 kg, hedef yaklaşık **%40 kaba / %60 kesif** (solver koridoru %37–43 kaba).
- **Besi Bitirme:** 450 kg ve üzeri, yem kalitesi ve rumen güvenliğine göre **%30–40 kaba / %60–70 kesif**, merkez hedef %35/%65.

Saman zorunlu değildir. Kaliteli kaba yem (yonca, silaj, uygun kuru ot) kaba yem hedefini ve eNDF ihtiyacını karşılayabiliyorsa saman 0 olabilir. Solver düşük kaliteli kaba yemi yalnız ucuz olduğu için yükseltmemeye devam eder.

## DEV4 test planı

Aynı yem havuzuyla 250 kg, 350 kg ve 500 kg canlı ağırlıkta çözüm alın. Kaba/kesif oranı, NDF/eNDF, toplam ve etkin nişasta, göreli asidoz riski, KM, HP, ME, NEm/NEg’den GCAA kapasitesi, Ca/P ve yem dağılımını karşılaştırın.

Ana program sürümü değişmedi: **v3.9.20**.

## DEV4.12–DEV4.13 yem sınırı ilkesi

Rasyon içindeki paylar KM bazında izlenir:
`(kg/baş/gün × KM oranı) / toplam rasyon KM`.

- DEV4.11’deki toplam tahıl, ticari yem ve buğday payı kuralları evrensel bilimsel sınır olmadıkları için kaldırılmıştır.
- Başlangıç/geliştirme/bitirme nişasta rakamları muhafazakâr çalışma ve dikkat bantlarıdır; tek başlarına klinik tanı veya evrensel fizyolojik üst sınır değildir.
- Yüksek nişasta ancak hızlı yıkılabilir nişasta ve etkili lif yetersizliğiyle birlikte ciddi güvenlik kapısına dönüşür.
- Yem Kataloğu → Düzenle ekranındaki etiket alt/üst dozları solver tarafından kesin uygulanır.
- Buğdayın tahıl KM payı %50’yi geçtiğinde işleme, adaptasyon, TMR ve kaba yem yönetimi için açık uyarı verilir; uygulama kendiliğinden %40 gibi bir oran uydurmaz.

Ayrıntılı hedef kartı düzeltmesi: `docs/SOLVER_DEV4_13_HEDEF_KARTLARI.md`.
Bilimsel veri katmanı ve model sınırları: `docs/SOLVER_DEV4_12_BILIMSEL_KATMAN.md`.


## v3.9.20 Solver DEV4.1 saha paketi
- Eski `🐄 ÇiftlikPro` marka yazısı korunur; masaüstü sol menüde ayrılan başlık kutusunda yatay ve dikey merkezlenir.
- Besi dönemi varsayılan olarak canlı ağırlıktan otomatik seçilir: <300 kg Başlangıç, 300–449 kg Geliştirme, 450+ kg Bitirme.
- İstenirse Rasyon Çöz ve hedef düzenleme ekranından Besi Başlangıç / Geliştirme / Bitirme manuel seçilebilir.
- KM bazında kaba/kesif koridorları: Başlangıç %47–53 kaba (merkez %50), Geliştirme %37–43 (merkez %40), Bitirme %30–40 (merkez %35).
- Ca/P hedef üstü cezası güçlendirildi; makro hedefleri korurken mineral taşmasını azaltmaya öncelik verir.
- GitHub Actions `windows-installer.yml` pakette korunmuştur. Kurulum EXE'si GitHub Actions artifact olarak üretilebilir.

### DEV4.9 saha UI notu
Bu paket DEV4.8 solver davranışını aynen korur. Değişiklik yalnız masaüstü sidebar logo konumu ve mobildeki işlevsiz hedef göster/gizle düğmesinin kaldırılmasıdır.

## DEV4.10 rapor ve hayvan aktarımı

Rasyon modülünde besi dönemine göre nişasta hedefi, üst güvenlik sınırı, rumenle birlikte canlı hedef kartı ve yazdırılabilir besin özeti bulunur. Solver nişastayı enerji, NDF/eNDF ve kaba/kesif dengesiyle birlikte değerlendirir.

- Tüm Hayvanlar raporu mobilde sıkışık geniş tablo yerine okunaklı hayvan kartları olarak gösterilir; web önizlemede de telefona özel kart düzeni ve doğrudan temiz PDF düğmesi bulunur.
- “Excel / PDF'den Hayvan İçe Aktar” alanı Raporlar sayfasının en üstündedir ve Veri Aktarımı sayfasında ayrıca belirgin bir kısayolu vardır.
- “Raporda Gösterilecek Sütunlar” seçimleri ekrandaki listeye, mobil kartlara, web önizlemeye, doğrudan PDF'ye ve Excel çıktısına birlikte uygulanır.
