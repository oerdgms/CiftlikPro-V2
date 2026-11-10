# ÇiftlikPro 2.0.52 — PWA kurulumu

Bu paket 2.0.51 üzerine hazırlanmıştır. Solver ve kayıt işlemleri korunur; geçmiş sorgular için indeksler eklenir.
Güncellemeden önce uygulamadan yedek alın; çalışan uygulamayı kapatıp yeni kaynak
klasörünü mevcut verilerinizin konumunu koruyarak çalıştırın. Veri klasörünü silmeyin.

## Ana ekrana ekleme

Giriş ekranında, Modüller sayfasının altında ve mobil yan menüde **Ana ekrana ekle**
bulunur. Buradaki rehber cihazınıza göre yönlendirme yapar.

- iPhone/iPad: HTTPS adresini Safari’de açın. Paylaş → Ana Ekrana Ekle.
  Görünüyorsa **Web Uygulaması Olarak Aç** açık olsun.
- Android: HTTPS adresini Chrome’da açın. Uygulamadaki **Uygulamayı yükle**
  düğmesi sunulduğunda kullanın; aksi halde Chrome menüsündeki **Uygulamayı yükle /
  Ana ekrana ekle** seçeneğini kullanın. Özel gezinme modundan çıkın.
- Bilgisayar: destekleyen tarayıcının uygulama yükleme simgesini kullanın.

Telefonun normal HTTP IP adresi (`http://100…:8953`) güvenli bağlam değildir.
Tam PWA/çevrimdışı bağlantı ekranı desteği için geçerli sertifikalı HTTPS gerekir.
Bilgisayardaki `http://localhost:8953` geliştirme istisnasıdır; telefondaki IP
adresini HTTPS yapmaz. Self-signed sertifika uyarısını geçmek yeterli değildir.

## Mevcut Tailscale bağlantısıyla HTTPS

1. ÇiftlikPro çiftlik bilgisayarında çalışıyor olsun. Bilgisayar ve telefon
   aynı Tailscale ağına bağlı olsun.
2. Bilgisayarda PowerShell açın ve önce mevcut yapılandırmayı görün:

   ```powershell
   tailscale serve status
   ```

   Kök HTTPS adresi başka bir uygulamaya ayrılmışsa onu değiştirmeyin. Boş bir
   HTTPS portu için Tailscale Serve belgelerinden uygun yapılandırmayı seçin.
3. Kök HTTPS adresi boşsa:

   ```powershell
   tailscale serve --bg 8953
   tailscale serve status
   ```

4. Komut HTTPS yetkisi için bir bağlantı verirse Tailscale hesabınızda açıp
   onaylayın. Gerekli yetkiniz yoksa ağ yöneticinizden isteyin.
5. Komutun gösterdiği gerçek `https://bilgisayar-adı.…ts.net` adresini telefonda
   açın. Host adını tahmin etmeyin; `https://100…:8953` yazmayın. Bu adres
   Tailscale ağınızdan erişilir; Funnel açmanız gerekmez.
6. Yeni HTTPS adresinde oturum açın; eski HTTP adresindeki oturum bu farklı
   adrese taşınmaz. Bu adresten ana ekrana ekleyin. Eski IP kısayolu varsa
   yenisini doğruladıktan sonra kaldırabilirsiniz.

Bu paket Tailscale ayarlarınızı otomatik değiştirmez. Bilgisayarın ve ÇiftlikPro’nun
açık, telefonun ağ/VPN bağlantısının etkin olması gerekir.

## Bağlantı kesilmesi ve güncelleme

İlk çevrimiçi açılışta bağlantı ekranı ve simgeler hazırlanır. Daha sonra bağlantı
kesilirse istenen sayfa adresi korunarak **Yeniden bağlan** ekranı gösterilir.
Çevrimdışıyken hayvan/finans kayıtları gösterilmez veya sıraya alınmaz.
Kayıt gönderdikten sonra bağlantı koptuysa tekrar göndermeden önce sunucudaki
kaydı kontrol edin.

**Ana ekrana ekle / Uygulama ve güncellemeler → Güncellemeyi kontrol et** ile
sunucudaki yeni sürümü kontrol edebilirsiniz. Yeni sürümde **Yeni sürümü aç**
görünür. Önce değişikliklerinizi kaydedin. Açık formlar otomatik yenilenmez.
Bu düğme sunucuya yeni paket indirmez veya kurmaz; sunucuda güncellenmiş sürümü açar.

Push bildirimi, mağaza paketi ve çevrimdışı veri düzenleme bu sürümün kapsamında değildir.

Kaynaklar:
- https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Making_PWAs_installable
- https://support.apple.com/guide/iphone/open-as-web-app-iphea86e5236/ios
- https://tailscale.com/docs/features/tailscale-serve
- https://tailscale.com/docs/reference/tailscale-cli/serve
