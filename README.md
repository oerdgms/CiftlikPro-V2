# ÇiftlikPro v3.9.21 DEV4 Hotfix2 — Aktif Sürü ve Zayiat Arşivi

Hotfix2, zayiat kaydı bulunan hayvanı aktif dişi/erkek/buzağı ve tüm aktif
hayvanlar listelerinden kesin olarak çıkarır. Önceki sürümde oluşmuş ancak
durumu aktif kalmış kayıtlar uygulama açılışında otomatik onarılır.

Ölen / Kayıp Hayvanlar arşivine `Düzenle` ve onaylı `Sil / Geri Al` işlemleri
eklendi. Düzenleme tarih, olay, neden, teşhis ve kurtarma gelirini değiştirince
maliyet ile otomatik finans bağlantılarını yeniden hesaplar. Sil/Geri Al yalnız
zayiatın oluşturduğu finans satırlarını kaldırır; hayvan alış ve gerçek tedavi
kayıtlarını korur, hayvanı yeniden aktif sürüye döndürür.

## Hotfix1 kapsamı

Hotfix1, ölüm/kayıp kaydında küpeye bağlı eski finans hareketlerini uzlaştırır.
Önceden giderleştirilmiş hayvan alımı ve tedavi ikinci kez yazılmaz. Rasyon,
bakım, henüz aktarılmamış tedavi ve diğer maliyetlerden yalnız eksik kalan tutar
Finans'a `Hayvan Ölümü / Zayiat` gideri olarak eklenir. Sigorta, et ve kurtarma
geliri ayrı gelir kaydıdır ve zayiat arşivindeki brüt kayıptan düşülür.

Doğrulama örneği: 100.000 TL alış önceden finanstayken 60 gün × 180 TL rasyon
ve henüz aktarılmamış 3.000 TL tedavi için yeni gider 13.800 TL; brüt ekonomik
kayıp 113.800 TL'dir. Tedavi de önceden finanstaysa yeni gider yalnız 10.800 TL olur.

## DEV4 kapsamı

V3.9.21 DEV4 ile dişi, erkek ve buzağıların alış bedeli; günlük yem, bakım ve
padok rasyon giderleri aynı maliyet motorunda birleştirilir. Ölüm, kayıp,
zorunlu imha veya işletmeden çıkış kaydı maliyeti olay tarihinde dondurur;
finansa nakit dışı zarar, varsa sigorta/kurtarma bedelini gelir olarak aktarır.
Ölen ve kayıp hayvanlar ayrı arşivde geçmiş kayıtları silinmeden korunur.

Finans ekranı nakit gelir-giderden ayrı bir `Zayiat / Zarar` toplamı gösterir;
böylece daha önce ödenmiş alış ve işletme giderleri ikinci kez nakit gider
sayılmaz.

DEV4.19.3 solver çekirdeği değiştirilmeden korunmuştur.

## Önceki DEV3 kapsamı

V3.9.21 DEV3; ilaç kataloğu, parti/lot ve son kullanma tarihi, stok hareketi,
hayvan/buzağı tedavi kaydı, doz ve uygulama yolu, et-süt arınma tarihleri ile
ilaç giderinin finansa aktarılmasını ekler. Katalog ürünleri tedavi önerisi
değildir; doz veteriner reçetesinden girilir. Arınma tarihi son uygulama ve
ürünün doğrulanmış asgari bekleme süresinden hesaplanır.

Kurulum, açık `CiftlikPro.exe` sürecini önce normal, gerekirse zorla kapatır;
dosya değişiminden önce yerel veritabanının tarihli güvenlik kopyasını alır ve
kurulum sonunda uygulamayı yeniden başlatabilir.

DEV4.19.3 solver çekirdeği değiştirilmeden korunmuştur.

DEV4.19.3, kaydedilmiş rasyon açıldığında tarayıcıdaki canlı hedef kartının
türetilmiş NEm/NEg yerine ham sıfır alanlarını okuyarak doğru GCAA değerini
ezmesini düzeltir. Sunucu özeti, canlı miktar değişimi ve rasyon simülasyonları
artık aynı normalize edilmiş besin değerlerini kullanır.

DEV4.19.2, kullanıcının gerçek yedeğinde görülen eksik enerji alanını düzeltir.
ME değeri bulunan fakat NEm/NEg alanları boş kullanıcı yemleri artık sıfır enerji
sayılmaz; yalnız eksik alanlar NRC tipi ME dönüşümüyle çalışma değerine çevrilir.
Gerçek analiz girilmiş alanlara dokunulmaz. Aynı yaklaşım eksik TDN ve kaba yem
eNDF alanlarında muhafazakâr çalışma değeri sağlar.

DEV4.19.1, 260 kg / 10 ay / 1,40 kg GCAA saha testinde görülen geç kayıt
reddini düzeltir. Ciddi kaba/kesif koridoru sapması artık yalnız sonuçta değil,
aday araması sırasında da sert raydır; solver güvenli koridordaki yem miktarı
kombinasyonlarını önceliklendirir.

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
# ÇiftlikPro v3.9.21 DEV2 — İlaç & Veteriner

İlaç ve veteriner ana ekranı saha kullanımına uygun özet + işlem çekmeceleri düzenindedir. Katalog, stok/SKT, tedavi, arınma ve finans bağlantısı aynı modülde izlenir. Katalog kaydı tedavi önerisi değildir; doz veteriner reçetesinden, arınma süresi Bakanlık ruhsat sorgusundaki güncel Ürün Özellikleri Özeti'nden doğrulanarak girilir.
