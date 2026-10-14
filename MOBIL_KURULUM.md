# ÇiftlikPro Enterprise — App Edition 2.0.5

Bu paket mevcut Windows uygulamanızın iPhone, iPad ve Android için mobil görünümünü içerir. Bilgisayar ve telefon aynı işletme verisini kullanır.

## Kurulum

1. Paketin tamamını GitHub kaynaklarına yükleyin. app klasörü, CiftlikPro.spec ve installer.iss birlikte güncellenmelidir.
2. Actions → CiftlikPro Windows Kurulum → Run workflow ile Windows kurulumunu oluşturun.
3. Oluşan CiftlikPro_Enterprise_V3_9_23_DEV4_AppEdition_2_0_5_Setup.exe dosyasını mevcut ÇiftlikPro bilgisayarına kurun.
4. ÇiftlikPro’yu bilgisayarda açın. Telefon aynı yerel ağa veya mevcut VPN bağlantınıza bağlı olsun.
5. Telefonda normal ÇiftlikPro adresini açın. Önceki görüşmemizdeki örnek: http://10.0.0.60:8953. Bilgisayarınızın IP adresi değiştiyse uygulamanın Ağ adresindeki yeni IP’yi kullanın.
6. Mevcut kullanıcı adınız ve şifrenizle giriş yapın.

Kaynak üzerinden çalıştırmak için mevcut KAYNAKTAN_CALISTIR.bat dosyası da kullanılabilir. Paket bir kaynak ve kurulum projesidir; hazır Windows EXE, Android APK veya iOS IPA içermez.

## Telefonda uygulama simgesi

- iPhone / iPad: Adresi Safari’de açın → Paylaş → Ana Ekrana Ekle. Görünüyorsa “Web Uygulaması Olarak Aç” seçeneğini etkinleştirin.
- Android: Adresi Chrome’da açın → Menü → Ana ekrana ekle. Tarayıcınızın sunduğu kurulum veya kısayol seçeneğini tamamlayın.
- İlk eklediğiniz simge normal kök adrese, yani :8953 adresine yönelsin.

Bu sürüm ana ekrana eklenebilen mobil web uygulamasıdır. Mağaza üzerinden dağıtılan bir native uygulama paketi değildir.

## Kullanım

- Alt menü: Ana Sayfa, Hayvanlar, İşler, Padoklar, Modüller.
- Mobil sayfa ekran genişliğinde sabit kalır; sağa-sola sürükleme ve sayfa yakınlaştırma kapalıdır. Finans raporundaki geniş tablo gibi özel alanlar gerektiğinde yalnız kendi kutusu içinde yatay kaydırılır.
- Yeşil + düğmesi bulunduğunuz ekranda yeni kayıt açar. Ana sayfada hızlı işlem menüsü açılır.
- Ana sayfadaki İşler sağlık görevleriyle vadeli ödemeleri birlikte gösterir. Ödeme satırı ilgili ödemenin mevcut finans ekranını açar.
- Hayvan satırındaki üç nokta kimlik bilgilerini ve mevcut Görüntüle / Düzenle / Sil işlemlerini açar.
- Hayvanlar ekranındaki yeşil `+` düğmesi yetişkin hayvan ve buzağı kaydını ayrı sunar. Buzağı kaydında doğum tarihi zorunludur ve mevcut 10 aydan küçük olma kuralı uygulanır.
- Hayvan listesinin Filtreler bölümünde padok, kayıt sayısı ve görünüm seçenekleri bulunur.
- Buzağı kartında kimlik üstte kompakt görünür; canlı maliyet ve finans özeti tam genişlikte alt alta yerleşir. Fotoğraf yükleme ile tartım kartları telefonda sıralı açılır ve tüm kayıt düğmeleri alt menünün üstünde erişilebilir kalır.
- Padok kartına dokununca padok ayrıntısı açılır. Üstteki geri oku padok listesine döndürür.
- Toplu hayvan taşı ekranında hayvanları ve hedef padoku seçin. Kapasite veya kayıt sorunu varsa seçimdeki hiçbir hayvan taşınmaz.
- Finans kartındaki üç nokta aynı kart içinde kompakt biçimde yer alır. Dokununca Düzenle/Sil düğmeleri ve kayıt ayrıntıları boş bant oluşturmadan açılır; finans kaydı başlığına dokunmak mevcut düzenleme ekranını açar.
- Modüller altında Finans, Yem & Stok, Rasyon, Hayvanlar, Padoklar, Sağlık, Üreme, Süt, Tarım, Raporlar ve Ayarlar bulunur.
- Diğer ekranlar ve sistem araçları bölümünde arşivler, veteriner/ilaç, performans, veri aktarımı, yedekleme ve yönetim bağlantıları bulunur.

## Bağlantı

İşlemler ÇiftlikPro bilgisayarındaki canlı sunucuya kaydedilir. Bilgisayarın açık ve erişilebilir olması gerekir.

Yerel HTTP bağlantısında mobil görünüm çalışır. HTTPS kullanıldığında destekleyen tarayıcılarda uygulama kurulum ve bağlantı kesilmesi ekranı da etkinleşir. Bağlantı yokken yeni kayıt yapılmaz ve eski finans/sağlık sayfaları çevrimdışı veri olarak gösterilmez.

## Resmî tarayıcı bilgileri

- [Apple: iPhone’da bir web sitesini uygulamaya dönüştürme](https://support.apple.com/en-ie/guide/iphone/iphea86e5236/27/ios/27)
- [MDN: Service Worker kullanımı ve güvenli bağlantı](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API/Using_Service_Workers)
