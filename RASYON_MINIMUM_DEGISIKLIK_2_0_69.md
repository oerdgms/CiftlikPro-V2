# Rasyonda En Az Değişiklik — AppEdition 2.0.69

## Sorun

Kayıtlı bir rasyonda yalnız canlı ağırlık veya KM hedefi değiştirildiğinde genel Akıllı Çözüm motoru reçeteyi yeni bir rasyon gibi yeniden optimize ediyordu. Besin hedefleri sağlansa bile seçilmiş yemlerin çoğu değişiyor ve kullanıcı mevcut uygulama düzenini kaybediyordu.

## Yeni davranış

- Genel **Akıllı Çözüm** yeni rasyon kurma davranışını korur.
- **Rasyonu Yeniden Hesapla** mevcut kg/baş/gün değerlerini referans olarak motora verir.
- Bilimsel ve güvenlik kapıları değişmez: KM, HP, NEm/NEg tabanlı GCAA, kaba/kesif faz koridoru, NDF/eNDF, nişasta ve mineral sınırları önce değerlendirilir.
- Bilimsel olarak eşdeğer adaylarda önce değişen yem satırı sayısı, sonra mevcut reçeteden toplam KM hareketi ve en büyük tekil değişim küçültülür. Maliyet bundan sonra gelir.
- Kilitli yemler değişmez. Normal yemlerde 0,04 kg'dan, katkılarda 0,005 kg'dan küçük sayısal sapmalar mevcut değere geri alınır ve veritabanına değişiklik olarak yazılmaz.
- İki ondalık yuvarlama GCAA kartını hedefin altına düşürürse yalnız zaten değişen bir satır mevcut değerine doğru en küçük adımla düzeltilir; yeni bir yem satırı gereksiz yere oynatılmaz.
- Önizleme, kaç yemin değiştiğini, kaçının aynen kaldığını ve toplam kg/baş/gün hareketini açıkça gösterir. Onay verilene kadar rasyon ve padok bağlantıları değişmez.

## Kullanıcının 270 → 300 kg örneği

Girdi:

- Hedef canlı ağırlık: 300 kg
- KM oranı: %2,75
- Hedef KM: 8,25 kg/gün
- Hedef GCAA kapasitesi: 1,80 kg/gün
- Mevcut rasyon: 8 yem, 9,02 kg KM/gün

Regresyon koşulu:

- En fazla 4 yem satırı anlamlı biçimde değişir.
- En az 4 yem satırı birebir korunur.
- Toplam miktar hareketi 4,00 kg/baş/günün altında kalır.
- KM hedefinin ±%3,5 bandı, otomatik besi fazının kaba/kesif koridoru ve en az 1,7995 kg/gün GCAA kapasitesi korunur.

Sonuç, mevcut reçeteyi körlemesine ölçeklemez. Faz veya güvenlik hedefi gerektiriyorsa yalnız gerekli yemler arasında besin takası yapar.

## Veri güvenliği

- Önizleme kullanıcıya özeldir ve 20 dakika sonra geçersiz olur.
- Önizlemeden sonra rasyon veya yem kataloğu değişmişse uygulama reddedilir.
- Aynı önizleme ikinci kez uygulanamaz.
- Geçmiş rasyon tarihleri ve padok bağlantıları korunur.

