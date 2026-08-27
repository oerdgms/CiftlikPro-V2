# ÇiftlikPro v3.9.20 Solver DEV1 — kalite ve kararlılık katmanı

Bu DEV, mevcut 6.17 hedef motorunu ve arayüzü değiştirmeden yalnız besi solver seçim davranışını iyileştirir.

## Değişiklikler
- Samanın toplam KM içinde aşırı büyümesini önleyen canlı ağırlık/faz tabanlı üst sınırlar.
- Tek bir tahılın rasyonu ele geçirmesini azaltan bireysel tahıl KM sınırları.
- Soya/kanola/ayçiçeği/pamuk küspelerinde legacy nişasta alanı hatasını solver içinde normalize eden güvenlik katmanı.
- Kaliteli protein yemlerinin yanlışlıkla yüksek nişastalı tahıl gibi cezalandırılması önlendi.
- Seçilen her normal yeme zorunlu minimum verme kaldırıldı; yem 0 olabilir, fakat anlamsız gramajlar cezalandırılır.
- Fizibilite aynı seviyedeyse maliyetten önce saha uygulanabilirliği ve yem kalite/denge puanı değerlendirilir.
- Düşük enerjili/yüksek NDF samanın KM doldurmak amacıyla baskınlaşmasına kalite cezası.
- Sonuç deterministik kalır (sabit RNG); aynı girdiler aynı çözüme yönelir.

## Değiştirilmeyenler
- NASEM hedef hesapları
- KM / HP / ME / kaba-kesif hedef kart toleransları
- Rumen pH, NDF/eNDF ve mineral güvenlik rayları
- DB, LAN, Tailscale, port ve UI

## Yerel karşılaştırma senaryosu
Aynı seçili yem havuzunda 270 / 350 / 500 / 600 kg besi erkek, 1.30 kg/gün hedef artış ile kontrol edildi. Yeni katman özellikle yüksek canlı ağırlıkta arpa samanı dominansını azaltıp ticari yem/protein kaynaklarına daha fazla alan açtı.

Not: Bu DEV saha doğrulaması içindir. Kullanıcının gerçek yem fiyatları ve analizleriyle eski/yeni solver sonuçları yan yana kontrol edilmeden final solver olarak kabul edilmemelidir.
