# DEV4.10 Rapor ve Hayvan Aktarımı

## Tüm Hayvanlar Raporu

- Raporlar ekranında aktif hayvanlar varsayılan olarak listelenir.
- Dişi, erkek, buzağı, durum, padok ve metin araması filtreleri desteklenir.
- Ana PDF düğmesi tarayıcı üstbilgi/URL alanlarından bağımsız, doğrudan üretilen A4 yatay raporu açar.
- Çok sayfalı PDF'de sütun başlıkları her sayfada tekrarlanır ve uygulama kontrollü sayfa numarası kullanılır.
- Web Önizleme düğmesi tarayıcı baskısı için ayrıca korunur.
- Excel çıktısı XLSX biçimindedir ve ekrandaki filtreleri aynen kullanır.
- Mobil rapor ekranı ve web önizleme, geniş tabloyu daraltmak yerine her hayvanı okunaklı bir kartta gösterir.
- Kullanıcı “Raporda Gösterilecek Sütunlar” bölümündeki tiklerle bilgi alanlarını açıp kapatabilir.
- Sütun seçimi ekran, mobil kart, web önizleme, doğrudan PDF ve XLSX çıktısında aynıdır; Küpe No her zaman korunur.

## Hayvan İçe Aktarma

- XLSX, CSV ve metin tablosu içeren dijital PDF desteklenir.
- PDF hedefi Tarım ve Orman Bakanlığı “İşletmede Bulunan Sığır ve Manda Türü Hayvan Raporu” biçimidir.
- Kayıt öncesinde hazır, uyarılı ve atlanacak satırlar önizlenir.
- Mevcut veya dosya içindeki mükerrer küpeler aktarılmaz.
- 10 aydan küçük hayvan, anne küpesi aktif dişi kayda bağlanabiliyorsa Buzağı olarak kaydedilir.
- Onaydan hemen önce tam güvenlik yedeği alınır.
- Dosya seçme alanı Raporlar sayfasının en üstündedir; Veri Aktarımı sayfasında da aynı işleme giden belirgin bir kısayol vardır.

## Rasyon Yazdırma

- Üst menü, komut şeridi, sol menü, sekme ve alt durum çubuğu çıktıda gizlenir.
- İşletme adı/logo, rapor tarihi ve işletme numarası yazdırma başlığında kullanılır.
- Tablo başlığı çok sayfalı çıktılarda tekrar eder ve yem satırları sayfa arasında bölünmez.
