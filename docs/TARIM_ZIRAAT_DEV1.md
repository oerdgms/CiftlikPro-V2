# Tarım & Ziraat DEV1 Kullanım ve Muhasebe Notları

## Amaç

Tarla üretimini hayvancılıktan ayrı bir işletme kolu olarak izlemek; buna
karşılık çiftlikte kullanılan mahsulün iki taraflı ve mükerrersiz kaydını
oluşturmaktır.

## Önerilen işlem sırası

1. **Tarlalar** ekranından özmal veya kiralık parseli kaydedin.
2. **Üretim Sezonları** ekranında yıl, ürün ve ekilen alanı tanımlayın.
3. **Girdi & Stok** ekranından tohum, gübre, tarım ilacı ve diğer girdilerin
   alışlarını girin.
4. **Tarla İşlemleri** ekranında sürüm, ikileme, ekim, gübreleme, ilaçlama,
   sulama ve hasat işçiliğini kaydedin. Kullanılan girdi stoktan düşer ve sezon
   maliyetine ağırlıklı ortalama maliyetle eklenir.
5. **Hasat & Mahsul** ekranında ürün ve yan ürünleri ayrı lotlar halinde stoğa
   alın.
6. Mahsul dışarı satılırsa **Dışarı Mahsul Satışı**, çiftlikte yem olarak
   kullanılacaksa **Hayvancılığa İç Transfer** işlemini kullanın.
7. **Tarım Raporları** ekranından sezon maliyeti, kg/dekar verim, TL/kg üretim
   maliyeti ve ekonomik sonucu kontrol edin.

## Muhasebe kuralları

| Olay | Tarım finansı | Hayvancılık finansı | Stok |
| --- | --- | --- | --- |
| Girdi satın alma | Gider | Etkilemez | Girdi artar |
| Girdiyi tarlada kullanma | İkinci gider oluşturmaz | Etkilemez | Girdi azalır |
| Tarla işlemi/işçilik | Gider | Etkilemez | Etkilemez |
| Hasat | Gelir oluşturmaz | Etkilemez | Mahsul artar |
| Dış satış | Gelir | Etkilemez | Mahsul azalır |
| Hayvancılığa iç transfer | İç satış geliri | Yem gideri | Mahsul azalır, yem artar |

İç transfer gerçek bir kasa/banka hareketi değildir. Bölüm kârlılığında iki
tarafta görünür; işletme geneli konsolide sonuçta birbirini götürür. Transfer
geri alındığında tarım geliri, hayvancılık gideri ve yem stok hareketi birlikte
geri alınır.

## Kontroller

- Yetersiz girdi veya mahsul stoku eksi bakiyeye düşürülemez.
- Kullanılmış bir girdi alışı, stok bakiyesini eksiye indirecekse silinemez.
- Çıkış yapılmış hasat lotu doğrudan silinemez; önce bağlı satış/transfer geri
  alınmalıdır.
- Otomatik oluşan finans kayıtları kaynak ekranından geri alınır; finans
  ekranında tek taraflı değiştirilmez.
- Kiralık tarla kira bedeli istenirse kayıt anında tarım finansına aktarılır.

## Sürüm güvencesi

Bu modül ayrı tablolar ve ayrı rota grubu kullanır. Mevcut hayvan, rasyon,
solver, ilaç/veteriner ve zayiat verileri taşınmaz ya da yeniden yazılmaz.
Uygulama açılışında yalnız eksik tarım tabloları güvenli biçimde oluşturulur.
