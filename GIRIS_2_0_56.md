# AppEdition 2.0.56 — Girişte işletme seçimi ve fotoğraf açılışı

Temel sürüm 2.0.55. Tarih: 01.11.2026. Kaynaktan çalıştırma paketi.

- Giriş ekranında İşletme alanı eklendi. Kullanıcı adı ve şifreyle giriş yapıldığında seçilen işletme doğrudan açılır.
- İşletme adları giriş ekranında görünür; hayvan, finans veya başka işletme kayıtları burada gösterilmez. Seçim tek başına yetki vermez: sunucu geçerli hesap, şifre ve işletme iznini kontrol eder. Yetkisiz işletmede oturum oluşturulmaz.
- Son başarılı işletme seçimi aynı tarayıcıda hatırlanır. Başarısız girişte seçim korunur. Alanı göndermeyen eski giriş istekleri ilk işletmeyi açmaya devam eder.
- Şifre kontrolü, eski şifre biçimini yükseltme, lisans kontrolü, oturum ve giriş günlüğü mevcut giriş işleyicisinde korunur. Kullanıcı yönetimi ve işletme ayrımı 2.0.55 ile aynıdır.
- Mobil fotoğraf artık sayfanın başında yüksek öncelikle istenir. İlk kare için aynı fotoğrafın 876 baytlık küçük önizlemesi HTML içine eklenir; tam fotoğraf beklenirken düz yeşil zemin yerine bu görünür. Formun açılması fotoğrafın bitmesine bağlı değildir.
- Tam fotoğraf dosyası değiştirilmedi. Küçük önizleme tam fotoğraf gelince netleşir. Mobil formun üst boşluğu yeni işletme alanına göre ayarlandı; şifre düğmesi ve PWA bağlantısı korunur.

Bilgisayarda mevcut veri konumuyla bu sürümü kaynaktan çalıştırın. Telefonda Uygulama ve güncellemeler bölümünden sürümü kontrol edip yenileyin. Uygulama simgesini yeniden kurmanız gerekmez.
