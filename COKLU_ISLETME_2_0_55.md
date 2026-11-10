# ÇiftlikPro AppEdition 2.0.55 — Birden fazla işletme

Temel: 2.0.54. Kaynaktan çalıştırma sürümü.

## İlk kullanım

1. Bilgisayardaki mevcut uygulamayı kapatın ve bu paketi ayrı bir klasöre açıp her zamanki kaynaktan çalıştırma yöntemiyle başlatın. Mevcut veri konumunu değiştirmeyin.
2. Sayfanın üst bölümündeki aktif işletme alanına veya mobil yan menüdeki İşletmeler · Değiştir bağlantısına dokunun.
3. Yönetici hesabıyla İşletme Ekle alanına adını yazıp Yeni İşletme Oluştur düğmesine basın.
4. Yeni işletme seçilir; başka işletmeye İşletmeyi Aç düğmesiyle geçebilirsiniz.
5. İşletme adını seçili işletmedeki İşletme Bilgileri ekranından düzenleyebilirsiniz.
6. Telefondaki Uygulama ve güncellemeler bölümünden sürümü kontrol edip yenileyin. Ana ekran simgesini yeniden yüklemek gerekmez.

Mevcut veritabanı ve fotoğraflar taşınmaz; ilk işletme olarak korunur. İlk işletmenin adı kayıtlı İşletme Bilgileri'nden alınır; ad boşsa İlk İşletmem görünür. Yeni işletmede eski hayvanlar, finans, stok hareketleri ve fotoğraflar bulunmaz. Mevcut uygulamanın standart yem kataloğu ve başlangıç rasyonları yeni işletmede hazırlanır.

## Ayrı kayıtlar, ortak hesaplar

Her işletmenin hayvan, buzağı, padok, sağlık, üreme, süt, tartım, yem/stok, rasyon, finans, tarım, rapor, ayar ve fotoğraf kayıtları kendi veritabanı/klasöründen okunur. Aynı küpe veya fotoğraf adı farklı işletmelerde bulunabilir.

Kullanıcı adı, şifre, aktif/pasif durum ve hesap rolü ortaktır. Kullanıcı Yönetimi ortak hesapları düzenler. Yöneticiler bütün işletmeleri yönetebilir. Eski erişim düzenini korumak için diğer kullanıcılar ilk işletmeye erişir; ek işletmeler için yönetici İşletmeler > Kullanıcı Erişimi alanından izin verir veya kaldırır. Sonraki istekte izin kontrol edilir. İşletmeye göre ayrı bir yönetici rolü tanımlanmaz.

Her sekmenin işletmesi URL/form/istek bilgisiyle korunur. Başka sekmede işletme değiştirildiğinde açık bir form kendiliğinden diğer işletmeye kaydetmez. İki cihaz farklı işletmelerde aynı anda çalışabilir. İşletme seçimi geçerli oturumda tutulur; yeniden girişte ilk işletmeden başlanır.

## Yedekleme ve geri yükleme

Yedek Al / Geri Yükle seçili işletmede çalışır. ZIP yedeklerde ve yeni JSON dışa aktarımlarında işletme kimliği bulunur. Kimliği başka işletmeye ait dosya reddedilir. Kimliksiz eski ZIP yedekleri ilk işletmeye aittir. Eski dış kaynak JSON içe aktarma işlevi korunur; işletme kimliği içermeyen böyle bir dosya, kullanıcı tarafından seçilmiş işletmeye aktarılır. JSON dışa aktarma tam fotoğraflı ZIP yedeğinin yerine geçmez.

Varsayılan yedek klasörleri işletmelere ayrıdır. Birden fazla işletmede aynı harici yedek klasörü seçilirse dosyalar o klasörün işletmeye özel alt klasörlerine konur. Açılıştaki otomatik yedekleme tanımlı işletmeleri ayrı ayrı yedekler. Geri yükleme sonrasında mevcut uygulamadaki gibi oturumlar kapanabilir.

## Veri konumu

Varsayılan Windows veri klasörü: %LOCALAPPDATA%\CiftlikPro. CIFTLIKPRO_DATA_DIR kullanılıyorsa mevcut özel konum korunur.

- İlk işletme: mevcut ciftlik.db, uploads ve backups.
- İşletme dizini/erişimleri: enterprises.sqlite3.
- Ek işletmeler: enterprises/f_<kimlik>/ altında ciftlik.db, uploads ve backups.
- İşletme dizini değişikliklerinden önce: enterprise-index-backups/enterprises-last.sqlite3 güvenlik kopyası.

Seçili işletmenin ZIP yedeği yalnız o işletmeyi içerir. Bütün kurulumu başka bilgisayara taşırken işletme dizini dahil veri klasörünün tamamı birlikte taşınmalıdır; tek bir işletmenin ZIP dosyası tüm işletmelerin listesi değildir.

2.0.53 fotoğraf önizlemeleri, 2.0.54 rozet düzeni ve önceki modül hızlandırmaları dahildir. Rasyon/finans hesap kuralları değiştirilmedi. EXE/APK/IPA bu pakette üretilmedi.
