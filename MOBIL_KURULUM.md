# ÇiftlikPro Enterprise — App Edition 2.0.42 Mobil Pilot Hazırlık

Bu paket mevcut Windows uygulamanızın iPhone, iPad ve Android için mobil görünümünü içerir. Bilgisayar ve telefon aynı işletme verisini kullanır.

## Kurulum

1. Paketin tamamını GitHub kaynaklarına yükleyin. app klasörü, CiftlikPro.spec ve installer.iss birlikte güncellenmelidir.
2. Actions → CiftlikPro Windows Kurulum → Run workflow ile Windows kurulumunu oluşturun.
3. Oluşan CiftlikPro_Enterprise_V3_9_23_DEV4_AppEdition_2_0_42_Setup.exe dosyasını mevcut ÇiftlikPro bilgisayarına kurun.
4. ÇiftlikPro’yu bilgisayarda açın. Telefon aynı yerel ağa veya mevcut VPN bağlantınıza bağlı olsun.
5. Telefonda normal ÇiftlikPro adresini açın. Yerel ağ örneği: http://10.0.0.60:8953. Bilgisayarınızın IP adresi değiştiyse uygulamanın Ağ adresindeki yeni IP’yi kullanın.
6. Mevcut kullanıcı adınız ve şifrenizle giriş yapın.

2.0.41 stabil paketini geri dönüş için saklayın. Güncellemeden önce uygulamanın mevcut yedekleme merkezinden yedek alın. Bu paket 2.0.41 tasarımını ve kayıt kurallarını koruyan pilot hazırlığıdır; gerçek cihaz/Windows kurulum onayı henüz tamamlanmış bir 2.1 kararlı sürüm değildir.

Kurulumdan sonra aynı sunucudaki `/app-build.json` adresi `2.0.42` ve `AppEdition2.0.42-MobilePilotPreparation` değerlerini göstermelidir. Bu adresin içeriğinde işletme kaydı veya şifre bulunmaz. Telefonda kayıt formunu kapatıp sayfayı yeniden açınca yeni kaynak adresleri kullanılır; güncelleme açık bir formu zorla yenilemez.

Pilot adımları ve sonuç sütunları: [MOBIL_PILOT_KONTROL.md](MOBIL_PILOT_KONTROL.md).

Kaynak üzerinden çalıştırmak için mevcut KAYNAKTAN_CALISTIR.bat dosyası da kullanılabilir. Paket bir kaynak ve kurulum projesidir; hazır Windows EXE, Android APK veya iOS IPA içermez.

## Telefonda uygulama simgesi

- iPhone / iPad: Adresi Safari’de açın → Paylaş → Ana Ekrana Ekle. Görünüyorsa “Web Uygulaması Olarak Aç” seçeneğini etkinleştirin.
- Android: Adresi Chrome’da açın → Menü → Ana ekrana ekle. Tarayıcınızın sunduğu kurulum veya kısayol seçeneğini tamamlayın.
- İlk eklediğiniz simge normal kök adrese, yani :8953 adresine yönelsin.

Bu sürüm ana ekrana eklenebilen mobil web uygulamasıdır. Mağaza üzerinden dağıtılan bir native uygulama paketi değildir.

## Kullanım

- Alt menü: Ana Sayfa, Hayvanlar, İşler, Padoklar, Modüller.
- Zil düğmesi ayrı Bildirimler listesini açar; masaüstündeki Bildirimler bağlantısı da aynı listeyi kullanır.
- Hayvan kartının Geçmiş sekmesi kayıt akışını gösterir. Satış ve zayiat işlemleri ayrı Satış / Zayiat sekmesinde korunur.
- Mobil İşletme Bilgileri ve Ayarlar bağlantısı işletme formunu açar; ikinci Dashboard açılmaz.
- Mobil sayfa ekran genişliğinde sabit kalır; sağa-sola sürükleme ve sayfa yakınlaştırma kapalıdır. Finans raporundaki geniş tablo gibi özel alanlar gerektiğinde yalnız kendi kutusu içinde yatay kaydırılır.
- Yeşil + düğmesi bulunduğunuz ekranda yeni kayıt açar. Ana sayfada hızlı işlem menüsü açılır.
- Ana sayfadaki İşler sağlık görevleriyle vadeli ödemeleri birlikte gösterir. Ödeme satırı ilgili ödemenin mevcut finans ekranını açar.
- Hayvan satırındaki üç nokta kimlik bilgilerini ve mevcut Görüntüle / Düzenle / Sil işlemlerini açar.
- Hayvan kartında Durum Ekle ve Doğum Ekle, masaüstüyle aynı hayvana bağlı pencereyi açar. Durum seçenekleri renkli ikonlarla listelenir; doğumda anne hazırdır. Vazgeç veya pencere dışına dokunarak kapatabilirsiniz.
- Hayvanlar ekranındaki yeşil `+` düğmesi yetişkin hayvan ve buzağı kaydını ayrı sunar. Buzağı kaydında doğum tarihi zorunludur ve mevcut 10 aydan küçük olma kuralı uygulanır.
- Hayvan listesinin Filtreler bölümünde padok, kayıt sayısı ve görünüm seçenekleri bulunur.
- Buzağı kartında kimlik üstte kompakt görünür; canlı maliyet ve finans özeti tam genişlikte alt alta yerleşir. Fotoğraf yükleme ile tartım kartları telefonda sıralı açılır ve tüm kayıt düğmeleri alt menünün üstünde erişilebilir kalır.
- Padok kartına dokununca padok ayrıntısı açılır. Üstteki geri oku padok listesine döndürür.
- Toplu hayvan taşı ekranında hayvanları ve hedef padoku seçin. Kapasite veya kayıt sorunu varsa seçimdeki hiçbir hayvan taşınmaz.
- Finans kartındaki üç nokta aynı kart içinde kompakt biçimde yer alır. Dokununca Düzenle/Sil düğmeleri ve kayıt ayrıntıları boş bant oluşturmadan açılır; finans kaydı başlığına dokunmak mevcut düzenleme ekranını açar.
- Modüller tek ızgarada 15 kutucuk sunar: Rasyon, Padoklar, Sağlık & Aşı, Üreme, Finans, Yem & Stok, Görevler, Raporlar, Ayarlar, Süt & Laktasyon, İlaç & Veteriner, Tarım Yönetimi, Hayvan Arşivi, Veri & Yedekleme, Senkronizasyon.

## Bağlantı

İşlemler ÇiftlikPro bilgisayarındaki canlı sunucuya kaydedilir. Bilgisayarın açık ve erişilebilir olması gerekir.

Yerel HTTP bağlantısında mobil görünüm çalışır. HTTPS kullanıldığında destekleyen tarayıcılarda uygulama kurulum ve bağlantı kesilmesi ekranı da etkinleşir. Bağlantı yokken yeni kayıt yapılmaz ve eski finans/sağlık sayfaları çevrimdışı veri olarak gösterilmez.

## Resmî tarayıcı bilgileri

- [Apple: iPhone’da bir web sitesini uygulamaya dönüştürme](https://support.apple.com/en-ie/guide/iphone/iphea86e5236/27/ios/27)
- [MDN: Service Worker kullanımı ve güvenli bağlantı](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API/Using_Service_Workers)

## Manuel laktasyon

Hayvanlar → Laktasyon Belirle → süt kaydı girdiğiniz 12 hayvanı seçin → Laktasyonda (Sağmal) → Kaydet. Başlangıcı bilmiyorsanız boş bırakın. Kartlar ve Sağmal filtresi kaydettiğiniz seçimi kullanır. Hayvan detayından tek kayıt değiştirilebilir. Kuruya çıkarma işlemi mevcut üreme kayıtlarıyla aynı tarihi kullanır.

## Ana Sayfa Düzeni ve Modüller

Ayarlar → Ana Sayfa Düzeni bağlantısını kullanın. Mobil bölümleri seçip oklarla sıralayabilir, sürü kartlarının görünürlüğünü ve ortak sırasını değiştirebilir, yaklaşan işlemlerde 3/5/10 satır seçebilirsiniz. Kaydetten sonra ana sayfaya dönün. Varsayılana Dön başlangıç düzenini getirir. Masaüstünün diğer dashboard kartları için düzenleyicideki Masaüstü kartlarını düzenle bağlantısını bilgisayardan açın.

Modüller ekranında tüm 15 kutucuk doğrudan görünür; diğer modüller grubunu açmak gerekmez. Bilgisayardan ana sayfadaki Modüller bağlantısı aynı ekranı açar.
