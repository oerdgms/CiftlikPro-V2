# Sunar 2026 gerçek ürün etiketleri

Bu kayıtlar kullanıcının gönderdiği 19–20 Ağustos 2026 üretim tarihli çuval
etiketlerinden alınmıştır. Çuval değerleri **ürün/yaş yem bazındadır**. Solverın
kullandığı HP, yağ, kül, sodyum ve enerji alanları, ürün için laboratuvar kuru
madde sonucu bulunmadığından `%88,35` referans KM kabulüyle dönüştürülmüştür.

Etikette bulunmayan KM, NDF, nişasta, Ca, P ve ileri rumen alanları üretici
analizi değildir. Bunlar katalogda açıkça referans tahmin olarak işaretlenir ve
laboratuvar analizi geldiğinde değiştirilmelidir.

## Sunar 15.26 Geliştirme Besi Yemi

- Etiket tarihi: 20/08/2026
- Ham protein: `%15,00`
- Ham yağ: `%3,00`
- Ham selüloz: `%9,27`
- Ham kül: `%7,73`
- Sodyum: `%0,27`
- Etikette okunabilen üst kullanım miktarı: `10 kg/baş/gün`
- Etiketin alt kullanım değeri kat yerinde kapalı olduğundan kesin alt sınır
  girilmemiştir.

Vitamin ve iz elementler (kg ürün başına):

- Vitamin A: `7.000 IU`
- Vitamin D3: `700 IU`
- Vitamin E: `30 mg`
- Manganez: `50 mg`
- Demir: `50 mg`
- Çinko: `50 mg`
- Bakır: `10 mg`
- İyot: `0,80 mg`
- Selenyum: `0,30 mg`
- Kobalt: `0,10 mg`

Üreticinin güncel resmi ürün adı `Sunar 15.26 Geliştirme Besi Yemi`dir. `2600
kcal/kg` enerji sınıfı ürün kodundan alınmıştır; gönderilen etiketin analitik
bileşenler bölümünde ME ayrıca yazmamaktadır. Bu nedenle enerji hesabı katalogda
kaynak açıklamasıyla birlikte türetilmiş değer olarak tutulur.

## Sunar Kardelen 19.27 Süt Yemi

- Etiket tarihi: 19/08/2026
- Ham protein: `%19,00`
- Ham yağ: `%3,50`
- Ham selüloz: `%9,07`
- Ham kül: `%6,89`
- Sodyum: `%0,33`
- Etiket kullanım miktarı: `6–12 kg/baş/gün`

Vitamin ve iz elementler (kg ürün başına):

- Vitamin A: `10.000 IU`
- Vitamin D3: `3.000 IU`
- Vitamin E: `40 mg`
- Manganez: `60 mg`
- Demir: `30 mg`
- Çinko: `80 mg`
- Bakır: `15 mg`
- İyot: `1,00 mg`
- Selenyum: `0,30 mg`
- Kobalt: `0,15 mg`

Etikette yem değişiminin kademeli yapılması, ürünün toplam rasyona karıştırılarak
3–4 öğünde verilmesi belirtilir. `2700 kcal/kg` enerji sınıfı, resmi ürün adı
`Kardelen 19.27` ve önceki resmi katalogla uyumludur; güncel etiketin analitik
bileşenler bölümünde ME ayrıca yazmamaktadır.

## Solver uygulaması

- Etikette bulunan HP, yağ, kül ve sodyum değerleri ürün bazından KM bazına
  çevrilmiştir.
- Besi yemi için `10 kg/baş/gün` üst sınırı kesin uygulanır.
- Kardelen süt yemi için `6–12 kg/baş/gün` etiketi süt solverında kesin uygulanır.
- NDF, nişasta, Ca/P ve KM tahminleri gerçek analiz gelene kadar solver veri
  kapsamı uyarısıyla korunur.
- Vitamin/iz element değerleri kayıt altındadır; mevcut solver bunları günlük
  gereksinim optimizasyonuna katmaz. Eksik bir mikro-mineral modeliyle otomatik
  premiks dozu üretmek güvenli kabul edilmez.
