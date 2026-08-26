# Süt Solver V1 – Referans Özeti

Kaynak referans: kullanıcı tarafından sağlanan `Sut_V5.01.xlsm` çalışma kitabındaki sağmal inek hesap yapısı ve INRA/NASEM yaklaşımı.

Bu GitHub paketine Excel dosyasının kendisi dahil edilmez. Yalnızca ÇiftlikPro içinde kullanılan sadeleştirilmiş hesap mantığı aktarılmıştır.

## Temel kullanıcı girdileri

- Canlı ağırlık (kg)
- Hedef süt miktarı (kg/gün)
- Elindeki yemler (mevcut ÇiftlikPro Yem Kataloğu)

## İç varsayımlar

- Süt yağı: %3,7
- Süt gerçek proteini: %3,1
- Orta laktasyon referansı: 100 DIM

## Ana hedefler

- Kuru madde tüketimi
- Ham protein yoğunluğu
- Metabolik enerji referansı
- Kaba/kesif yem oranı

Güvenlik kontrolleri: NDF, eNDF, nişasta, tahmini rumen pH, Ca ve P.

## DMI yaklaşımı

Süt_V5.01 içindeki sağmal inek DMI yapısından sadeleştirilmiştir:

`DMI = ((BW^0.75 * 0.0968) + (0.372 * FCM) - 0.293) * (1 - exp(-0.192 * (DIM/7 + 3.67)))`

FCM için 4% yağ düzeltilmiş süt yaklaşımı kullanılır.
