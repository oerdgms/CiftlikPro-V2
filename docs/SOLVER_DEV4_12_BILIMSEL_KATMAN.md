# Solver DEV4.12 — Bilimsel Katman, Sınırlar ve Saha Doğrulaması

## Sonuç

DEV4.12 tek bir sistemi diğerinin adıyla taklit etmez. Aktif besi gereksinim çekirdeği **NASEM 2016** olarak kalır. **INRA 2018** yem değerleri ayrı alanlarda tutulur ve yalnız veri mevcutsa yem doğrulaması, veri kapsamı ve rumen fermantasyon riskinde kullanılır. **CNCPS** ise karbonhidrat/protein fraksiyonları ve geçiş hızları eksik olduğu için bu sürümün aktif hesap motoru olarak gösterilmez.

## Kaynaklardan koda taşınan kararlar

| Konu | DEV4.12 davranışı | Gerekçe |
|---|---|---|
| Enerji ve büyüme | NEm bakım + NEg büyüme arzından karşılanabilir GCAA hesaplanır. | ME kartının yakın olması tek başına hedef canlı ağırlık artışını garanti etmez. |
| Rumen güvenliği | Toplam nişasta, bilinen nişasta yıkılabilirliği, NDF/eNDF ve veri kapsamı birlikte yorumlanır. | Asidoz riski yalnız nişasta yüzdesinden veya tek bir lif denkleminden belirlenemez. |
| pH | Klinik/tahmini pH sayısı gösterilmez; göreli risk sınıfı gösterilir. | Rumen pH’sı öğün düzeni, tamponlama, emilim, adaptasyon, işleme ve bireysel değişkenlikten etkilenir. |
| Tahıl/buğday | Evrensel sert yüzde yoktur; %50 üzeri buğday tahıl KM payı açık saha uyarısıdır. | Kaynaklar işleme ve adaptasyona bağlı farklı oranlar bildirir; tek oran tüm rasyonlara uygulanamaz. |
| Ticari yem | Varsayılan yapay grup yüzdesi yoktur. Girilmiş etiket alt/üst dozu kesindir. | Gerçek sınır ürün formülü ve etiketidir. |
| Uygun olmayan çözüm | Güvensiz, hedef GCAA’yı ciddi kaçıran, temel hedeflerden ikisini ciddi kaçıran veya hedef büyümeyi aşırı KM ile telafi eden reçete kaydedilmez. | Profesyonel formülasyon yazılımlarındaki fizibilite ve “limiting constraints” yaklaşımı. |
| Maliyet | Güvenlik ve fizibiliteden sonra karşılaştırılır. | Ucuz fakat hedefi karşılamayan rasyon çözüm değildir. |

## Nişasta bantlarının anlamı

Başlangıç `20–24`, geliştirme `23–27`, bitirme `25–29` yüzdeleri **KM bazında muhafazakâr çalışma hedefidir**. Geriye uyumlu `starch_max` alanındaki `28/30/31` değerleri uyarı eşiğidir; evrensel fizyolojik üst sınır değildir ve tek başına reçeteyi reddetmez.

Çözüm ancak yüksek toplam/etkin nişasta sinyali etkili lif yetersizliğiyle birleştiğinde “yüksek göreli asidoz riski” nedeniyle engellenir. Yıkılabilirlik verisi düşük kapsamlıysa sonuç “düşük güven” olarak işaretlenir.

## Yem Kataloğu yeni alanları

- Nişasta rumen yıkılabilirliği (%), NDF sindirilebilirliği (%)
- RDP ve RUP (% HP)
- INRA UFV, PDI, PDIA, RPB ve doluluk birimi
- İşleme biçimi
- Etiket/uzman alt ve üst dozu (kg/baş/gün)
- Doz sınırının kaynağı

`0`, veri bilinmiyor anlamındadır. Kullanıcının laboratuvar veya etiket verisi, uygulamanın referans değerinden üstündür. DEV4.12 yalnız açıkça eşleşen standart arpa, buğday ve mısır kayıtlarına INRA referansı ekler; mevcut sıfırdan büyük kullanıcı değerini ezmez.

## Bu sürümde bilinçli olarak yapılmayanlar

- “CNCPS çalışıyor” iddiası yoktur. Tam CNCPS için en az CHO A/B1/B2/B3/C, protein A/B/C, RDP/RUP, geçiş ve sindirim hızları, çevre/hayvan girdileri gerekir.
- INRA UFV ile NASEM NEm/NEg aynı sütunda toplanmaz veya katsayıyla birbirine çevrilmez.
- eNDF’den klinik rumen pH tahmini yapılmaz.
- Buğdayın yanında arpayı otomatik olarak belirli bir yüzdeye zorlayan evrensel kural yoktur. İşletme stratejisi gerekiyorsa yem etiket/uzman sınırları girilmelidir; göreli tahıl karışımı kuralı ayrıca kullanıcı tercihi olarak tasarlanmalıdır.
- Bu yazılım veteriner tanısı veya bağımsız besleme uzmanı onayı yerine geçmez.

## Kaynaklar

- NASEM, *Nutrient Requirements of Beef Cattle, 8th Revised Edition*: https://nap.nationalacademies.org/catalog/19014/nutrient-requirements-of-beef-cattle-eighth-revised-edition
- INRAE, INRAtion V5 / Ruminal: https://www.inration-ruminal.fr/en/inration-v5-ruminal/
- INRAE animal feed tables: https://www.inrae.fr/en/news/animal-feed-tables
- INRA/CIRAD/AFZ parameter definitions and feed tables: https://www.feedtables.com/content/parameters?parameter_cat=77
- Cornell CNCPS overview: https://cals.cornell.edu/animal-science/outreach-extension/publications-resources-software/cncps
- NorFor model overview: https://www.norfor.info/the-model/the-norfor-model/
- AMTS optimizer/limiting-constraint features: https://agmodelsystems.com/our-products/product-pricing/
- Manitoba Agriculture, wheat feeding and adaptation guidance: https://www.gov.mb.ca/agriculture/livestock/beef/wheat-feeding-wheat-to-cattle-.html
- MSD Veterinary Manual, subacute ruminal acidosis: https://www.msdvetmanual.com/digestive-system/diseases-of-the-ruminant-forestomach/subacute-ruminal-acidosis-in-cattle-and-sheep
- Chibisa et al. (2020), barley-based feedlot diets and roughage/acidosis trade-off: https://academic.oup.com/jas/article/98/6/skaa160/5843592
- Pereira et al. (2021), peNDF/uNDF and finishing steers: https://academic.oup.com/tas/article/5/1/txaa236/6062483
- Coon & Tucker (2025), continuous reticulorumen pH and individual/management variation: https://academic.oup.com/jas/article/doi/10.1093/jas/skaf058/8058575

## Saha test kontrolü

1. Aynı yem havuzuyla 250, 350 ve 500 kg senaryolarını çözün.
2. NEm/NEg’den “rasyon enerji kapasitesi” ile hedef GCAA’yı karşılaştırın.
3. Toplam nişasta ile etkin rumen nişastasını ve veri güvenini birlikte okuyun.
4. Ticari yemlerin gerçek etiket üst dozunu Yem Kataloğu’na girin.
5. Buğday/arpada işleme biçimini ve laboratuvar değerlerini kaydedin.
6. Çözüm reddedilirse belirtilen sınırlayan kısıtı düzeltmeden maliyet optimizasyonuna geçmeyin.
7. Geçiş rasyonunu ve adaptasyon planını sahada veteriner/besleme uzmanıyla doğrulayın.
