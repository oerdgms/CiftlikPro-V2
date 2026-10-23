# ÇiftlikPro Enterprise — App Edition 2.0.30

Sağlık Yönetimi, mobil ve masaüstünde aynı kayıtları kullanan tek bir merkez oldu.
Temel: 2.0.29 Mobil Liste Sadeleştirme + Senkronizasyon.

## Yeni ekran

- Genel Bakış: Bugün, Geciken, Yaklaşan (30 gün) ve Tedavide sayıları gerçek kayıtlardan hesaplanır.
- Aşı, Parazit, Vitamin / Mineral, Hastalık / Tedavi ve Senkronizasyon aynı sayfadan açılır.
- Planlananlar ve Yapılanlar ayrı listelerdir. Küpe, ad, padok ve işlem aranabilir.
- Aylık Sağlık Takvimi; seçilen günün planlarını ve geçmiş kayıtlarını birlikte gösterir.
- Genel Bakış'ta hasta hayvanlar ve son uygulamalar bulunur.
- Modüller ve mobil menüde tek Sağlık Yönetimi girişi vardır. Senkronizasyon ile ilaç/veteriner araçlarına buradan erişilir. Diğer modüller korunmuştur.

## Sağlık işlemi ekleme

1. Sağlık Yönetimi → Sağlık İşlemi Ekle.
2. Kategoriyi ve listeden işlem adını seçin veya yeni bir ad yazın.
3. İlk uygulama tarihini, gerekiyorsa gün/ay tekrarını ve rapel süresini girin.
4. Tek veya birden fazla hayvan seçin. Padok filtresinden sonra Görünenleri seç ile toplu seçim yapabilirsiniz. Arama ve cinsiyet filtresi birlikte çalışır.
5. Plan oluştur seçimi yalnız görev açar. Yapılan uygulamayı kaydet seçimi gerçek geçmiş uygulamasını kaydeder.

Planlar hayvan kimliklerini saklar. Sonradan padoka giren hayvanlar eski plana kendiliğinden katılmaz. Padok değiştiren veya buzağılıktan hayvan listesine geçen kayıtlar planlarını korur.

## Tekrar, rapel ve uygulama

- Süreler kullanıcı tarafından belirlenir; aşı adına bağlı otomatik tıbbi doz veya süre atanmaz.
- Tekrar aralığı 0 ise tek seferliktir. Ay ve gün hesabı ayrıdır; ay sonu tarihleri doğru ele alınır.
- İlk uygulama Yapıldı olarak kaydedilince rapel gerçek uygulama tarihine göre güncellenir ve varsa bir sonraki tekrar planlanır. Böylece hayvan bazında bir sonraki dönem takip edilir.
- Rapel ilk uygulama tamamlanmadan kaydedilemez. Gelecekteki tarih yapılmış gibi kaydedilemez.
- Hastalık / Tedavi → Takip Planı ile çok günlük, X günde bir ve günde birden fazla uygulamalı plan da oluşturulabilir.
- Tamamlama yalnız seçilen hayvanın ilgili uygulamasını işler. Tekrarlanan gönderimler ikinci sağlık kaydı veya gider oluşturmaz.
- Uygulama tutarı, gerçek uygulama tamamlandığında finansa ve hayvanın sağlık geçmişine aynı kayıtla yansır.

## Hastalık / tedavi

Hastalık tarihi, belirti/teşhis ve hayvan seçimiyle kayıt açılır. Veteriner, tutarlar ve notlar isteğe bağlıdır. Girilen toplam tutar seçilen hayvanlara kuruş farkı kaybolmadan dağıtılır. Harici ilaç/tedavi tutarı, stoktan kullanılan ilaçlardan ayrı tutulur; stoklu tedavi, mevcut İlaç Stoku ve Tedaviler ekranından yönetilir.

İyileşti ve Yeniden aç işlemleri geçmişi korur. Hastalık düzenlemesi bağlı gideri günceller; Sil işlemi yalnız o hastalık kaydını ve ona ait giderleri kaldırır.

## Düzenleme ve çıktı

- Programlar düzenlenebilir, duraklatılabilir ve kaldırılabilir. Program kaldırıldığında yapılan uygulamalar korunur.
- Uygulaması yapılmış programların hayvan ve takvim bilgileri korunur; ad, maliyet ve notlar düzenlenebilir.
- Yapılan uygulamanın adı, tutarı ve açıklaması düzenlenebilir. Tarih düzeltmesi için uygulama geri alınıp doğru tarihle tekrar kaydedilir. Bağlı sonraki uygulama yapılmışsa önce o kayıt geri alınmalıdır.
- Liste başlığındaki üç nokta: seçili kategori/filtre için Yazdır ve PDF indir.
- Mevcut sağlık, gebelik aşısı, senkronizasyon, stok, arınma ve veteriner kayıtları korunur.

## Kurulum

Bu ZIP tam kaynak paketidir. GitHub Actions / Inno Setup çıktısının adı:
`CiftlikPro_Enterprise_V3_9_23_DEV4_AppEdition_2_0_30_Setup.exe`

Mevcut veri klasörünüzü silmeyin. Normal güncelleme kurulumunda veritabanı şeması uygulama açılışında güncellenir. Mobil ve masaüstü aynı sunucu adresini kullanır; yeni bölüm Modüller → Sağlık Yönetimi içindedir.
