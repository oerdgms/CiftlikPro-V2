# Solver DEV4.13 — Bilimsel Hedef Kartları

## Hotfix 1 — saha ekranı tutarlılığı

- GCAA kapasitesi minimum hedefin %0,5'ten fazla altındaysa yeşil “Yeterli” yerine gerçek açık yüzdesi gösterilir.
- Fiziksel etkili NDF yeterli, fakat kaba yem KM payı faz koridorunun altındaysa iki ölçüt birbirine karıştırılmaz.
- İdeal nişasta üst sınırının ilk 0,5 puan üzeri “Sınırda” kabul edilir; tek başına göreli asidoz riskini yükseltmez.
- Ticari yemin etiket üst dozu bilinmiyorsa sistem güvenli sınıra ulaşıldığını iddia etmez; katalog dozunun tamamlanmasını ister.
- Uzun çözüm mesajları mobilde özetlenir ve ayrıntıları açılır biçimde sunulur.

## Düzeltilen temel hata

Önceki hedef motoru `animal_type` değerini kullanıcıdan kaydediyor fakat hesapta
kullanmıyordu. Bu nedenle “Besi Erkek”, düve ve kastre erkek aynı gereksinim
profiliyle hesaplanıyordu. DEV4.13 aşağıdaki ayrımı yapar:

| Kullanıcı seçimi | Hesap profili | NASEM referansı |
|---|---|---|
| Besi Erkek (Tosun / Boğa) | Kastre edilmemiş büyüyen erkek | Chapter 20, Table 20-2 |
| Düve | Büyüyen/bitirilen sığır | Chapter 20, Table 20-1 |
| Kastre Erkek | Büyüyen/bitirilen sığır | Chapter 20, Table 20-1 |

## Kartların yeni anlamı

| Kart | Gereksinim yorumu | Başarı ölçütü |
|---|---|---|
| KM tüketimi | Diyetin NEm yoğunluğuna bağlı tahmin | Tahmine yakınlık |
| GCAA kapasitesi | NEm bakımdan ayrıldıktan sonra kalan NEg arzı | Hedef GCAA'yı karşılama |
| Ham protein | Chapter 20 diyet değerlendirme taban değeri | Minimumu karşılama |
| Ca ve P | Bakım + büyüme gereksinimi | Minimum + güvenlik üst penceresi |
| ME | Ayrıntıda bilgi amaçlı | Tek başına büyüme kararı değildir |
| Nişasta / eNDF | Faz çalışma bandı ve rumen risk sinyali | Birlikte değerlendirme |

HP, Ca ve P'nin gereksinimin biraz üzerinde olması “hedef yanlış” veya
“formülasyon başarısız” anlamına gelmez. Çok yüksek arz maliyet, azot yükü ve
mineral güvenlik penceresi açısından ayrıca uyarılır.

## 500 kg / 1,30 kg-gün kontrol noktası

“Besi Erkek (Tosun / Boğa)” profiliyle yaklaşık değerler:

- NEm gereksinimi: 9,08 Mcal/gün
- NEg gereksinimi: 4,78 Mcal/gün
- MP gereksinimi: 775 g/gün
- HP tarama tabanı: %9,96 KM
- Kalsiyum minimumu: 44,5 g/gün
- Fosfor minimumu: 23,3 g/gün

KM tüketimi sabit bir sayı değildir; rasyonun NEm yoğunluğuna göre canlı yeniden
hesaplanır. Bu yüzden aynı hayvan için daha yoğun ve daha seyrek iki rasyonun KM
kartında farklı gereksinim görülebilir.

## Kaynaklar

- National Academies, *Nutrient Requirements of Beef Cattle, Eighth Revised Edition* (2016): https://nap.nationalacademies.org/catalog/19014/nutrient-requirements-of-beef-cattle-eighth-revised-edition
- Chapter 20 Table 20-1 ve 20-2 errata: https://nap.nationalacademies.org/resource/19014/Beef%20Cattle%20errata%20sheet2.pdf

Bu modül karar desteğidir; laboratuvar analizi, yem işleme biçimi, adaptasyon,
sağlık ve saha gözlemi olmadan klinik tanı veya veteriner reçetesi üretmez.
